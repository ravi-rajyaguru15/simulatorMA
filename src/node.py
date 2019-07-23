from offloadingDecision import offloadingDecision 
import constants 
from job import job

import sys 
# from Queue import Queue

class node:
	# message = None
	decision = None
	jobQueue = None
	taskQueue = None
	resultsQueue = None
	index = None
	nodeType = None

	totalEnergyCost = None

	def __init__(self, queue, index, nodeType):
		self.decision = offloadingDecision()
		self.jobQueue = list()
		self.taskQueue = list()
		self.resultsQueue = queue
		self.index = index
		self.nodeType = nodeType

		self.totalEnergyCost = 0

	def setOffloadingDecisions(self, options):
		self.decision.options = options

	def busy(self):
		return len(self.jobQueue) > 0
	# def prependTask(self, subtask):
	# 	self.jobQueue = [subtask] + self.jobQueue

	def maybeAddNewJob(self):
		# possibly create new job
		if constants.uni.evaluate(constants.JOB_LIKELIHOOD): # 0.5 

			self.createNewJob()

	def createNewJob(self):
		self.jobQueue.append(job(self, constants.SAMPLE_SIZE.gen(), self.decision))
		print "new task"

	def addTask(self, task):
		self.taskQueue.append(task)


	def updateTime(self):
		# if no jobs available, perhaps generate one
		# print len(self.jobQueue)

		# check if there's something to be done now 
		if len(self.taskQueue) > 0:
			currentTask = self.taskQueue[0]



			# do process and check if done
			currentTask.tick()
			if currentTask.finished:
			# 	print 'job done'
				
			# 	self.resultsQueue.put([currentTask.samples, currentTask.computeResult()])

				self.taskQueue = self.taskQueue[1:]
				
				# if isinstance ()
				# print "finish on first job done"
				# sys.exit(0)

			# print current
		# else:
		# 	print "no jobs available"





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
