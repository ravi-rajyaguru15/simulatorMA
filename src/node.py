from offloadingDecision import offloadingDecision 
import constants 
from task import task

# from Queue import Queue

class node:
	# message = None
	decision = None
	jobQueue = None
	resultsQueue = None

	def __init__(self, queue):
		self.decision = offloadingDecision()
		self.jobQueue = list()
		self.resultsQueue = queue

	def setOffloadingDecisions(self, options):
		self.decision.options = options


	def updateTime(self):
		# if no jobs available, perhaps generate one
		# if len(self.jobQueue) == 0:
		# 	print "no jobs"

		# possibly create new job
		if constants.uni.evaluate(constants.JOB_LIKELIHOOD): # 0.5 
			self.jobQueue.append(task(self, samples=constants.SAMPLE_SIZE.gen()))
			print "new task"

		# print len(self.jobQueue)
		# check if there's a job now 
		if len(self.jobQueue) > 0:
			current = self.jobQueue[0]

			# check if undecided
			if current.destination is None:
				self.decision.chooseDestination(current)

			# do process and check if done
			if current.process():
				print 'job done'
				
				self.resultsQueue.put([current.samples, current.computeResult()])

				self.jobQueue = self.jobQueue[1:]

			# print current
		# else:
		# 	print "no jobs available"



	# def sendTo(this, destination):
	# 	latency = this.mcu.messageOverheadLatency.gen() + this.mrf.rxtxLatency(this.message.size)
	# 	energy = this.mcu.overheadEnergy() + this.mrf.txEnergy(this.message.size)

	# 	res = destination.receive(this.message)
	# 	this.message = None

	# 	return result(latency, energy) + res
    
	# def receive(this, message):
	# 	this.message = message;
	# 	# reception does not add latency
	# 	return result(latency=0, energy=this.mcu.activeEnergy(this.mrf.rxtxLatency(this.message.size) + this.mrf.rxEnergy(this.message.size)))



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
