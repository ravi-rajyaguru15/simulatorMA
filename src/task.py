from warnings import warn

import constants 
import subtask
from result import result
# from node import node

class task:
	size = None
	samples = None
	startTime = None
	host = None
	destination = None

	subtasks = None
	subtaskIndex = None
	currentSubTask = None

	finished = None

	def __init__(self, origin, size=None, samples=None):
		self.host = origin

		if samples is None:
			# if size is None:
			warn("Must supply samples to create message")
				# warn("Must supply size or samples to create message")
			# self.size = size
			# self.samples = None
		else:
			# self.size = samples * constants.SAMPLE_RAW_SIZE.gen()
			self.samples = samples
		
		self.finished = False


	def setDestination(self, decision):
		self.destination = decision

		# populate subtasks based on types of devices
		if self.host is self.destination:
			print 'local processing'
			# local processing
			self.subtasks = [(subtask.processing(self.host, self.samples))]
			self.subtaskIndex = 0
		elif self.destination.nodeType == constants.ELASTIC_NODE:
			print ("offloading to other elastic node")
			self.subtasks = [
				subtask.communication(self.host, self.rawMessageSize()),
				# subtask.processing(self.host, self.samples),
				# subtask.communication(self.destination, self.processedMessageSize())
			]
		else:
			raise Exception("Other destination not implemented")
			print 'UNIMPLEMENTED'

	def process(self):
		# figure out which subtask is active
		if self.currentSubTask is None:
			# more subtasks available?
			if self.subtaskIndex >= len(self.subtasks):
				self.finished = True
				return True
			else:
				# if task requires a destination, wait until destination is available
				nextSubTask = self.subtasks[self.subtaskIndex]

				# if not dependent on destination, always start
				destinationReady = True
				if nextSubTask.destination is not None:
					# check if destination of message has something to do 
					if nextSubTask.destination.busy():
						destinationReady = False
						print "destination is not ready!"
					# create new task for receiving device
					else:
						nextSubTask.destination.addSubTask(subtask.communication())
						nextSubTask.destination.addSubTask(subtask.communication())
						nextSubTask.destination.addSubTask(subtask.communication())
						# nextSubTask.destination.prependTask(subtask.communication())

				if destinationReady:
					self.currentSubTask = nextSubTask

		# progress subtask 
		self.currentSubTask.tick()

		if self.currentSubTask.finished:
			self.subtaskIndex += 1
			self.currentSubTask = None

	def computeResult(self):
		output = result()

		for sub in self.subtasks:
			output += result(latency=sub.totalDuration, energy=sub.energyCost)

		return output

	# def rawMessageSize(self):
	# 	return self.samples * constants.SAMPLE_PROCESSED_SIZE.gen()

	def processedMessageSize(self):
		return self.samples * constants.SAMPLE_PROCESSED_SIZE.gen()


	# # change message from raw to processed
	# def process(self):
	# 	# if self.samples is None:
	# 	# 	warn("Cannot process message without sample count")
	# 	# self.size = self.samples * constants.SAMPLE_PROCESSED_SIZE.gen()
