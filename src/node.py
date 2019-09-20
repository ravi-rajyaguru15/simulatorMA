from offloadingDecision import offloadingDecision 
import constants 
from job import job

import sys 
import numpy as np 

class node:
	# message = None
	decision = None
	jobQueue = None
	taskQueue = None
	currentTask = None
	resultsQueue = None
	index = None
	nodeType = None

	totalEnergyCost = None
	drawLocation = None

	components = None
	waitingForResult = None
	jobActive = None
	alwaysHardwareAccelerate = None

	# busy = None

	def __init__(self, queue, index, nodeType, components, alwaysHardwareAccelerate=None):
		self.decision = offloadingDecision()
		self.jobQueue = list()
		print ("jobqueue", self.jobQueue)
		self.taskQueue = list()
		self.resultsQueue = queue
		self.index = index
		self.nodeType = nodeType

		self.totalEnergyCost = 0
		
		self.drawLocation = (0,0)

		self.components = components

		self.waitingForResult = False
		self.jobActive = False
		self.alwaysHardwareAccelerate = alwaysHardwareAccelerate

		# self.processors = list()

	def setOffloadingDecisions(self, options):
		self.decision.options = options

	def busy(self):
		# busy if any are busy
		return self.jobActive # or self.waitingForResult or np.any([device.busy for device in self.components])
		# return len(self.jobQueue) > 0
	# def prependTask(self, subtask):
	# 	self.jobQueue = [subtask] + self.jobQueue

	def maybeAddNewJob(self):
		# possibly create new job
		if constants.uni.evaluate(constants.JOB_LIKELIHOOD): # 0.5 
			print ("\t\t** new task ** ")
			self.createNewJob()

	def createNewJob(self, hardwareAccelerated=None):
		# if not set to hardwareAccelerate, use default
		if hardwareAccelerated is None:
			hardwareAccelerated = self.alwaysHardwareAccelerate
			# if still None, unknown behaviour
		assert(hardwareAccelerated is not None)
		self.jobQueue.append(job(self, constants.SAMPLE_SIZE.gen(), self.decision, hardwareAccelerated=hardwareAccelerated))

	def addTask(self, task):
		self.taskQueue.append(task)


	def updateTime(self):
		# if no jobs available, perhaps generate one
		# print len(self.jobQueue)

		# check if there's something to be done now 
		if len(self.taskQueue) > 0:
			self.currentTask = self.taskQueue[0]

			# do process and check if done
			self.currentTask.tick()
			if self.currentTask.finished:
			# 	print 'job done'
				
			# 	self.resultsQueue.put([currentTask.samples, currentTask.computeResult()])
				self.currentTask = None
				self.taskQueue = self.taskQueue[1:]

		# remove finished jobs
		if len(self.jobQueue) > 0:
			currentJob = self.jobQueue[0]

			# check if job is finished
			if currentJob.finished:
				print ('job done')
				
			# 	self.resultsQueue.put([currentTask.samples, currentTask.computeResult()])

				self.jobQueue = self.jobQueue[1:]
				
				# if isinstance ()
				# print "finish on first job done"
				# sys.exit(0)

			# print current


	# def offloadElasticNode(this, samples):
	# 	this.ed.message = message(samples=samples)

	# 	# offload to elastic node
	# 	res = this.ed.sendTo(this.en)
	# 	res += this.en.process(accelerated=True)
	# 	res += this.en.sendTo(this.ed)
	# 	# print 'offload elastic node:\t', res

	# 	return res



	# def offloadPeer(this, samples):
	# 	# offload to neighbour
	# 	this.ed.message = message(samples=samples)
	# 	res = this.ed.sendTo(this.ed2)
	# 	# print res
	# 	res += this.ed2.process()
	# 	# print res
	# 	res += this.ed2.sendTo(this.ed)
	# 	# print res
	# 	# print 'offload p2p:\t\t\t', res

	# 	return res

	# def offloadServer(this, samples):

	# 	# offload to server
	# 	this.ed.message = message(samples=samples)
	# 	res = this.ed.sendTo(this.gw)
	# 	res += this.gw.sendTo(this.srv)
	# 	res += this.srv.process()
	# 	res += this.srv.sendTo(this.gw)
	# 	res += this.gw.sendTo(this.ed)
	# 	# print 'offload server:\t\t\t', res

	# 	return res