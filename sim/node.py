import sim.offloadingDecision
import sim.constants
from sim.job import job
from sim.fpga import fpga
import sim.processor
import sim.debug

import sys
import time
import numpy as np
from collections import deque

class node:
	# message = None
	decision = None
	jobQueue = None
	taskQueue = None
	currentJob = None
	numJobs = None
	currentSubtask = None
	simulation = None
	# resultsQueue = None
	index = None
	# nodeType = None

	energyLevel = None
	totalEnergyCost = None
	averagePower = None
	powerCount = None
	totalSleepTime = None
	drawLocation = None

	platform = None
	components = None
	processors = None
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

	def __init__(self, simulation, platform, index, components, alwaysHardwareAccelerate=None):
		self.platform = platform

		self.decision = sim.offloadingDecision.offloadingDecision(self, sim.systemState.current)
		self.simulation = simulation
		self.jobQueue = list()
		sim.debug.out ("jobqueue" + str(self.jobQueue))
		self.taskQueue = deque()

		# self.resultsQueue = queue
		self.index = index
		# self.nodeType = nodeType

		self.energyLevel = node.convertEnergy(platform.BATTERY_SIZE, platform.BATTERY_VOLTAGE)
		self.averagePower = 0
		self.powerCount = 0
		self.totalEnergyCost = 0
		self.totalSleepTime = 0

		self.drawLocation = (0,0)

		self.setComponents(components)

		# self.waitingForResult = False'
		self.jobActive = False
		self.numJobs = 0
		self.alwaysHardwareAccelerate = alwaysHardwareAccelerate

		self.batch = dict()
		# self.batchProcessing = False # indicates if batch has been full (should process batch)

		# self.processors = list()

	def setComponents(self, components):
		if components is None:
			return
		self.components = components
		self.processors = [component for component in self.components if isinstance(component, sim.processor.processor)]
		for processor in self.processors:
			processor.timeOutSleep()


	@staticmethod
	# convert mAh to Joule
	def convertEnergy(mah, voltage):
		return mah * voltage * 3.6


	def __repr__(self):
		return str(type(self)) + " " + str(self.index)

	# def setOptions(self, options):
		# self.setOffloadingDecisions(options)

	def setOffloadingDecisions(self, devices):
		self.decision.setOptions(devices)

	def hasFpga(self):
		return np.any([isinstance(component, fpga) for component in self.processors])

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
		self.numJobs += 1
		self.jobQueue.append(job)

	# appends one job to the end of the task queue (used for queueing future tasks)
	def addSubtask(self, task, appendLeft=False):
		task.owner = self
		if appendLeft:
			self.taskQueue.appendleft(task)
		else:
			self.taskQueue.append(task)

		# if nothing else happening, start task
		self.nextTask()

	# # add follow-up task when one task is finished, used for state progression
	# def addSubtask(self, task):
	# 	task.owner = self
	# 	sim.debug.out("switching from {} to {}".format(self.currentTask, task))

	# 	self.currentTask = task

	def removeTask(self, task):
		sim.debug.out("REMOVE TASK {0}".format(task))
		self.taskQueue.remove(task)
		sim.debug.out("{} {}".format(self.currentSubtask, task))
		if self.currentSubtask is task:
			self.currentSubtask = None
			sim.debug.out ("next task...")
			self.nextTask()

	def nextTask(self):
		# only change task if not performing one at the moment
		if self.currentSubtask is None:
			# check if there is another task is available
			if len(self.taskQueue) > 0:
				# do receive tasks first, because other device is waiting
				for task in self.taskQueue:
					if isinstance(task, sim.subtask.rxMessage):
						self.currentSubtask = task
						self.taskQueue.remove(task)
						break
				# if still nothing, do a normal task
				if self.currentSubtask is None:
					# if any of the tasks have been started continue that
					for task in self.taskQueue:
						if task.started:
							self.currentSubtask = task
							self.taskQueue.remove(task)
							break
					
					# lastly, see if tx messages are available
					if self.currentSubtask is None:
						# do receive tasks first, because other device is waiting
						for task in self.taskQueue:
							if isinstance(task, sim.subtask.txMessage):
								self.currentSubtask = task
								self.taskQueue.remove(task)
								break

						# if nothing else to do, just do the oldest task that isn't a new job
						if self.currentSubtask is None:
							self.currentSubtask = self.taskQueue.popleft()

				if len(self.taskQueue) > 1:
					sim.debug.out("")
					sim.debug.out("nextTask: {} {}".format(self.currentSubtask, self.taskQueue))
					sim.debug.out("")
					
				# self.currentTask = self.taskQueue[0]
				# remove from queue because being processed now
				# self.taskQueue.remove(self.currentTask)

				self.currentSubtask.owner = self
				sim.debug.out (str(self) + " NEXT TASK " + str(self.currentSubtask))

			else:
				# sim.debug.out("no next task")
				self.currentSubtask = None

	# try another task if this one is stuck
	def swapTask(self):
		sim.debug.out(self, "SWAPPING TASK\n\n\n\n")
		if sim.debug.enabled: 
			time.sleep(.1)
		# move current task to queue to be done later
		self.addSubtask(self.currentSubtask) # current task not None so nextTask won't start this task again
		self.currentSubtask = None
		self.nextTask()

	def asleep(self):
		for component in self.components:
			# if anything awake, device not sleeping
			if not component.isSleeping():
				return False
		# if it gets here, nothing is awake
		return True


	# calculate the energy at the current activity of all the components
	def energy(self, duration=sim.constants.TD):
		# totalPower = 0
		# for component in self.components:
			# totalPower += component.power()
		
		# calculate total power for all components
		totalPower = 0
		for component in self.components:
			totalPower += component.power()

		if totalPower >= 1:
			sim.debug.out("massive power usage!")
			# sim.debug.enabled = True
		self.updateAveragePower(totalPower)
		incrementalEnergy = totalPower * duration
		self.totalEnergyCost += incrementalEnergy
		# TODO: assuming battery powered
		# print (incrementalEnergy)
		self.energyLevel -= incrementalEnergy
		return incrementalEnergy

	def updateAveragePower(self, power):
		self.powerCount += 1
		# 1/n
		# self.averagePower += 1.0 / self.powerCount * (power - self.averagePower) 
		# alpha
		self.averagePower += sim.constants.EXPECTED_LIFETIME_ALPHA * (power - self.averagePower)
		# sim.debug.out("average power: {}, {}".format(power, self.averagePower))

	def updateTime(self, currentTime):
		# if no jobs available, perhaps generate one
		asleepBefore = self.asleep()

		# see if there's a job available
		self.nextJob(currentTime)

		# check if there's something to be done now
		if self.currentSubtask is None:
			self.nextTask()

		# do process and check if done
		if self.currentSubtask is not None:
			self.currentSubtask.tick()

		# check for idle sleep trigger
		for component in self.components:
			if isinstance(component, sim.processor.processor):
				component.timeOutSleep()
 

		asleepAfter = self.asleep()

		if asleepBefore and asleepAfter:
			self.totalSleepTime += sim.constants.TD
	
	def expectedLifetime(self):
		# estimate total life time based on previous use
		if self.averagePower == 0:
			return np.inf
		else:
			return self.energyLevel / self.averagePower

	def setCurrentBatch(self, job):
		if job.hardwareAccelerated:
			self.currentBatch = job.currentTask
		else:
			self.currentBatch = 0
		sim.debug.out("Setting current batch to {} ({})".format(self.currentBatch, job), 'b')
		# time.sleep(.5)

	def addJobToBatch(self, job):
		if job.hardwareAccelerated:
			task = job.currentTask
		else:
			# 0 task indicates software solutions
			task = 0

		# create list if new task
		if task not in self.batch.keys():
			self.batch[task] = list()
		
		self.batch[task].append(job)
	
	def maxBatchLength(self):
		# investigate batch if not empty
		if self.batch:
			longestBatch = np.argmax([len(item) for key, item in self.batch.items()])
			return len(self.batch[list(self.batch.keys())[longestBatch]]), longestBatch
		else:
			return 0, 0

	def batchLength(self, task):
		# return batch length for a specific task
		if task in self.batch:
			return len(self.batch[task])

	def nextJobFromBatch(self):
		if self.currentJob is None:
			# print([len(self.batch[batch]) > 0 for batch in self.batch])
			# if len(self.batch) > 0:
			# print ("keys", self.batch.keys())
			maxBatchLength, maxBatchIndex = self.maxBatchLength()
			if maxBatchLength > 0:
				# check current batch
				if self.currentBatch is None:
					# batch first job in batch
					if self.batch.keys() is not None:
						self.currentBatch = list(self.batch.keys())[maxBatchIndex]
						# TODO: must keep going until all batches are empty
						sim.debug.out("starting batch {}".format(self.currentBatch))

				sim.debug.out ("grabbed job from batch")
				# if self.currentBatch not in self.batch.keys():
				# 	print ("Batch does not exist in node", self.batch, self.currentBatch)
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
		sim.debug.out("batch before remove {}".format(self.batch))
		if job in self.batch[self.currentBatch]:
			self.batch[self.currentBatch].remove(job)

		else:
			raise Exception("Could not find job to remove from batch")
		sim.debug.out("batch after remove {}".format(self.batch))



	def nextJob(self, currentTime):
		if self.currentJob is None:
			if len(self.jobQueue) > 0:
				sim.debug.out ("grabbed job from queue")
				self.currentJob = self.jobQueue[0]
				self.jobQueue.remove(self.currentJob)
				# see if it's a brand new job
				if not self.currentJob.started:
					self.currentJob.start(currentTime, self.batchLength(self.currentJob.currentTask))
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
