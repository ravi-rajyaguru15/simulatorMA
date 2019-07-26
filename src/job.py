from warnings import warn

import constants 
import subtask
from result import result
# from node import node

class job:
	datasize = None
	samples = None
	startTime = None
	creator = None
	processor = None

	hardwareAccelerated = None

	# subtasks = None
	# subtaskIndex = None
	# currentSubTask = None

	# finished = None

	def __init__(self, origin, samples, offloadingDecision, hardwareAccelerated):
		self.creator = origin
		self.samples = samples
		# initialise message size to raw data
		self.datasize = self.rawMessageSize()
		
		self.setProcessor(offloadingDecision.chooseDestination(self))
		# self.finished = False
		self.hardwareAccelerated = hardwareAccelerated

	def setProcessor(self, processor):
		self.processor = processor

		# populate subtasks based on types of devices
		if self.creator is self.processor:
			print ('local processing')
			# local processing
			self.creator.addTask(subtask.processing(self, self.processor.fpga))
			# otherwise we have to send task
		else:
			# elif self.destination.nodeType == constants.ELASTIC_NODE:
			print ("offloading to other device")
			self.creator.addTask(subtask.createMessage(self))
			# subtask.communication(self.host, self.rawMessageSize()))

	def process(self):
		print ("PANIC")
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
						print ("destination is not ready!")
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

	def rawMessageSize(self):
		return self.samples * constants.SAMPLE_PROCESSED_SIZE.gen()

	def processedMessageSize(self):
		return self.samples * constants.SAMPLE_PROCESSED_SIZE.gen()


	# # change message from raw to processed
	# def process(self):
	# 	# if self.samples is None:
	# 	# 	warn("Cannot process message without sample count")
	# 	# self.size = self.samples * constants.SAMPLE_PROCESSED_SIZE.gen()
