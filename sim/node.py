from sim.offloadingDecision import offloadingDecision
import sim.constants
from sim.job import job
from sim.fpga import fpga
import sim.processor
import sim.debug

import sys
import time
import numpy as np

class node:
	# message = None
	decision = None
	jobQueue = None
	taskQueue = None
	currentJob = None
	currentTask = None
	resultsQueue = None
	index = None
	# nodeType = None

	totalEnergyCost = None
	totalSleepTime = None
	drawLocation = None

	platform = None
	components = None
	# waitingForResult = None
	jobActive = None
	alwaysHardwareAccelerate = None

	batch = None
	currentBatch = None
	batchFull = None

	# busy = None

	# drawing
	rectangle = None
	location = None

	def __init__(self, platform, queue, index, components, alwaysHardwareAccelerate=None):
		self.platform = platform

		self.decision = offloadingDecision(self)
		self.jobQueue = list()
		sim.debug.out ("jobqueue" + str(self.jobQueue))
		self.taskQueue = list()

		self.resultsQueue = queue
		self.index = index
		# self.nodeType = nodeType

		self.totalEnergyCost = 0
		self.totalSleepTime = 0

		self.drawLocation = (0,0)

		self.components = components

		# self.waitingForResult = False'
		self.jobActive = False
		self.alwaysHardwareAccelerate = alwaysHardwareAccelerate

		self.batch = dict()
		# self.batchProcessing = False # indicates if batch has been full (should process batch)

		# self.processors = list()

	def __repr__(self):
		return str(type(self)) + " " + str(self.index)

	# def setOptions(self, options):
		# self.setOffloadingDecisions(options)

	def setOffloadingDecisions(self, devices):
		self.decision.setOptions(devices)

	def hasFpga(self):
		return np.any([isinstance(component, fpga) for component in self.components])

	def hasJob(self):
		# busy if any are busy
		return self.currentJob is not None

		# return self.jobActive # or self.waitingForResult or np.any([device.busy for device in self.components])
		# return len(self.jobQueue) > 0
	# def prependTask(self, subtask):
	# 	self.jobQueue = [subtask] + self.jobQueue

	def maybeAddNewJob(self, currentTime):
		# possibly create new job
		if sim.constants.uni.evaluate(sim.constants.JOB_LIKELIHOOD): # 0.5
			sim.debug.out ("\t\t** {} new job ** ".format(self))
			self.createNewJob(currentTime)

	def createNewJob(self, currentTime, hardwareAccelerated=None, taskGraph=None):
		# if not set to hardwareAccelerate, use default
		if hardwareAccelerated is None:
			hardwareAccelerated = self.alwaysHardwareAccelerate
			# if still None, unknown behaviour
		assert(hardwareAccelerated is not None)

		self.addJob(job(currentTime, self, sim.constants.SAMPLE_SIZE.gen(), self.decision, hardwareAccelerated=hardwareAccelerated, taskGraph=taskGraph))
		sim.debug.out("added job to queue", 'p')

	def addJob(self, job):
		self.jobQueue.append(job)

	def addTask(self, task):
		task.owner = self
		self.taskQueue.append(task)

		# if nothing else happening, start task
		self.nextTask()

	def removeTask(self, task):
		sim.debug.out("REMOVE TASK {0}".format(task))
		self.taskQueue.remove(task)
		sim.debug.out("{} {}".format(self.currentTask, task))
		if self.currentTask is task:
			self.currentTask = None
			sim.debug.out ("next task...")
			self.nextTask()

	def nextTask(self):
		if self.currentTask is None:
			if len(self.taskQueue) > 0:
				self.currentTask = self.taskQueue[0]
				# remove from queue because being processed now
				self.taskQueue.remove(self.currentTask)

				self.currentTask.owner = self
				sim.debug.out (str(self) + " NEXT TASK " + str(self.currentTask))

			else:
				sim.debug.out("no next task")
				self.currentTask = None

	# try another task if this one is stuck
	def swapTask(self):
		print(self, "SWAPPING TASK\n\n\n\n")
		time.sleep(.1)
		# move current task to queue to be done later
		self.addTask(self.currentTask) # current task not None so nextTask won't start this task again
		self.currentTask = None
		self.nextTask()

	def asleep(self):
		return np.all([component.isSleeping() for component in self.components])

	# calculate the energy at the current activity of all the components
	def energy(self, duration=sim.constants.TD):
		totalPower = np.sum([component.power() for component in self.components])
		return totalPower * duration

	def updateTime(self, currentTime):
		# if no jobs available, perhaps generate one
		asleepBefore = self.asleep()

		# see if there's a job available
		self.nextJob(currentTime)

		# check if there's something to be done now
		if self.currentTask is None:
			self.nextTask()

		# do process and check if done
		if self.currentTask is not None:
			self.currentTask.tick()

		# check for idle sleep trigger
		for component in self.components:
			if isinstance(component, sim.processor.processor):
				component.timeOutSleep()
 

		asleepAfter = self.asleep()

		if asleepBefore and asleepAfter:
			self.totalSleepTime += sim.constants.TD

	def setCurrentBatch(self, job):
		if job.hardwareAccelerated:
			self.currentBatch = job.taskGraph[0]
		else:
			self.currentBatch = 0

	def addJobToBatch(self, job):
		if job.hardwareAccelerated:
			task = job.taskGraph[0]
		else:
			# 0 task indicates software solutions
			task = 0

		# create list if new task
		if task not in self.batch.keys():
			self.batch[task] = list()
		
		self.batch[task].append(job)
	
	def maxBatchLength(self):
		return np.max([len(item) for key, item in self.batch.items()])

	def nextJobFromBatch(self):
		if self.currentJob is None:
			# print([len(self.batch[batch]) > 0 for batch in self.batch])
			# if len(self.batch) > 0:
			if self.maxBatchLength() > 0:
				sim.debug.out ("grabbed job from batch")
				self.currentJob = self.batch[self.currentBatch][0]
				self.removeJobFromBatch(self.currentJob)

				return self.currentJob
			else:
				sim.debug.out("No more jobs in batch", 'c')
				# self.batchProcessing = False
				self.currentJob = None
				self.currentBatch = None

		return None

	def removeJobFromBatch(self, job):
		print("batch before remove", self.batch)
		if job in self.batch[self.currentBatch]:
			self.batch[self.currentBatch].remove(job)

		else:
			raise Exception("Could not find job to remove from batch")
		print("batch after remove", self.batch)



	def nextJob(self, currentTime):
		if self.currentJob is None:
			if len(self.jobQueue) > 0:
				sim.debug.out ("grabbed job from queue")
				self.currentJob = self.jobQueue[0]
				self.jobQueue.remove(self.currentJob)
				# see if it's a brand new job
				if not self.currentJob.started:
					self.currentJob.start(currentTime)
				else:
					sim.debug.out("\tALREADY STARTED")



	def removeJob(self, job):
		sim.debug.out("REMOVE JOB")
		# sim.debug.out ('{} {}'.format(self.jobQueue, job))
		# try to remove from queue (not there if from batch)
		if job in self.jobQueue:
			self.jobQueue.remove(job)
		# set as not current job
		if self.currentJob is job:
			self.currentJob = None

		# sim.debug.out ('{} {}'.format(self.jobQueue, job))
		sim.debug.out (self.currentJob)
	# def offloadElasticNode(this, samples):
	# 	this.ed.message = message(samples=samples)

	# 	# offload to elastic node
	# 	res = this.ed.sendTo(this.en)
	# 	res += this.en.process(accelerated=True)
	# 	res += this.en.sendTo(this.ed)
	# 	# sim.debug.out 'offload elastic node:\t', res

	# 	return res



	# def offloadPeer(this, samples):
	# 	# offload to neighbour
	# 	this.ed.message = message(samples=samples)
	# 	res = this.ed.sendTo(this.ed2)
	# 	# sim.debug.out res
	# 	res += this.ed2.process()
	# 	# sim.debug.out res
	# 	res += this.ed2.sendTo(this.ed)
	# 	# sim.debug.out res
	# 	# sim.debug.out 'offload p2p:\t\t\t', res

	# 	return res

	# def offloadServer(this, samples):

	# 	# offload to server
	# 	this.ed.message = message(samples=samples)
	# 	res = this.ed.sendTo(this.gw)
	# 	res += this.gw.sendTo(this.srv)
	# 	res += this.srv.process()
	# 	res += this.srv.sendTo(this.gw)
	# 	res += this.gw.sendTo(this.ed)
	# 	# sim.debug.out 'offload server:\t\t\t', res

	# 	return res
