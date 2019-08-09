from sim.offloadingDecision import offloadingDecision 
import sim.constants 
from sim.job import job
import sim.debug

import sys 
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
	nodeType = None

	totalEnergyCost = None
	drawLocation = None

	components = None
	# waitingForResult = None
	jobActive = None
	alwaysHardwareAccelerate = None

	batch = None
	batchFull = None

	# busy = None

	def __init__(self, queue, index, nodeType, components, alwaysHardwareAccelerate=None):
		self.decision = offloadingDecision()
		self.jobQueue = list()
		sim.debug.out ("jobqueue" + str(self.jobQueue))
		self.taskQueue = list()
		self.resultsQueue = queue
		self.index = index
		self.nodeType = nodeType

		self.totalEnergyCost = 0
		
		self.drawLocation = (0,0)

		self.components = components

		# self.waitingForResult = False
		self.jobActive = False
		self.alwaysHardwareAccelerate = alwaysHardwareAccelerate

		self.batch = list()
		self.batchProcessing = False # indicates if batch has been full (should process batch)

		# self.processors = list()

	def __repr__(self):
		return str(type(self)) + " " + str(self.index)

	def setOffloadingDecisions(self, options):
		self.decision.options = options

	def hasJob(self):
		# busy if any are busy
		return self.currentJob is not None
		# return self.jobActive # or self.waitingForResult or np.any([device.busy for device in self.components])
		# return len(self.jobQueue) > 0
	# def prependTask(self, subtask):
	# 	self.jobQueue = [subtask] + self.jobQueue

	def maybeAddNewJob(self):
		# possibly create new job
		if sim.constants.uni.evaluate(sim.constants.JOB_LIKELIHOOD): # 0.5 
			sim.debug.out ("\t\t** new task ** ")
			self.createNewJob()

	def createNewJob(self, currentTime, hardwareAccelerated=None):
		# if not set to hardwareAccelerate, use default
		if hardwareAccelerated is None:
			hardwareAccelerated = self.alwaysHardwareAccelerate
			# if still None, unknown behaviour
		assert(hardwareAccelerated is not None)
		
		self.jobQueue.append(job(currentTime, self, sim.constants.SAMPLE_SIZE.gen(), self.decision, hardwareAccelerated=hardwareAccelerated))
		sim.debug.out("added job to queue", 'p')

	def addTask(self, task):
		self.taskQueue.append(task)

		# if nothing else happening, start task
		self.nextTask()

	def removeTask(self, task):
		sim.debug.out ("REMOVE TASK {0}".format(task))
		self.taskQueue.remove(task)
		sim.debug.out ("{} {}".format(self.currentTask, task))
		if self.currentTask is task:
			self.currentTask = None
			sim.debug.out ("next task...")
			self.nextTask()

	def nextTask(self):
		if self.currentTask is None:
			if len(self.taskQueue) > 0:
				sim.debug.out (str(self) + "NEXT TASK")
				self.currentTask = self.taskQueue[0]
				self.currentTask.owner = self



	# calculate the energy at the current activity of all the components
	def energy(self, duration=sim.constants.TD):
		totalPower = np.sum([component.power() for component in self.components])
		return totalPower * duration

	def updateTime(self, currentTime):
		# if no jobs available, perhaps generate one
		# sim.debug.out len(self.jobQueue)

		# see if there's a job available
		self.nextJob(currentTime)

		# check if there's something to be done now 
		if self.currentTask is None:
			self.nextTask()


		# do process and check if done
		if self.currentTask is not None:
			self.currentTask.tick()
			# if self.currentTask.finished:
			# 	sim.debug.out ("\033[34mTask done\033[0m")
				
			# # 	self.resultsQueue.put([currentTask.samples, currentTask.computeResult()])
			# 	self.currentTask = None
			# 	self.taskQueue = self.taskQueue[1:]

		
			# check if job is finished
			# if currentJob.finished:
			# 	sim.debug.out ('job done')
				
			# # 	self.resultsQueue.put([currentTask.samples, currentTask.computeResult()])

			# 	self.jobQueue = self.jobQueue[1:]
				
				# if isinstance ()
				# sim.debug.out "finish on first job done"
				# sys.exit(0)

			# sim.debug.out current

	def nextJobFromBatch(self):
		if self.currentJob is None:
			if len(self.batch) > 0:
				sim.debug.out ("grabbed job from batch")
				self.currentJob = self.batch[0]

				return self.currentJob

		return None

	def removeJobFromBatch(self, job):
		if job in self.batch:
			self.batch.remove(job)

		else:
			raise Exception("Could not find job to remove from batch")

	
	def nextJob(self, currentTime):
		if self.currentJob is None:
			if len(self.jobQueue) > 0:
				sim.debug.out ("grabbed job from queue")
				self.currentJob = self.jobQueue[0]
				# see if it's a brand new job
				if not self.currentJob.started:
					self.currentJob.start(currentTime)



	def removeJob(self, job):
		sim.debug.out("REMOVE JOB")
		sim.debug.out ('{} {}'.format(self.jobQueue, job))
		self.jobQueue.remove(job)
		if self.currentJob is job:
			self.currentJob = None

		sim.debug.out ('{} {}'.format(self.jobQueue, job))
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
