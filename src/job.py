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
	processingNode = None
	processor = None

	hardwareAccelerated = None

	finished = None

	processed = None
	taskGraph = None
	currentTask = None

	def __init__(self, origin, samples, offloadingDecision, hardwareAccelerated, taskGraph=None):
		self.creator = origin
		self.samples = samples
		# initialise message size to raw data
		self.datasize = self.rawMessageSize()
		self.hardwareAccelerated = hardwareAccelerated
		
		# self.finished = False
		self.processed = False
		self.finished = False
		if taskGraph is None:
			taskGraph = constants.DEFAULT_TASK_GRAPH
		self.taskGraph = taskGraph

		# start at first task
		self.currentTask = self.taskGraph[0]
		# initiate task by setting processing node
		self.setprocessingNode(offloadingDecision.chooseDestination(self))

	def setprocessingNode(self, processingNode):
		self.processingNode = processingNode

		print ("setprocessingnode")

		self.setProcessor(processingNode)
		# populate subtasks based on types of devices
		if not self.offloaded():
			# local processing
			if self.hardwareAccelerated:
				# check if fpga already configured
				if self.processingNode.fpga.isConfigured(self.currentTask):
					self.processingNode.addTask(subtask.mcuFpgaOffload(self))
				else:
					self.processingNode.addTask(subtask.reconfigureFPGA(self))
			else:
				self.creator.addTask(subtask.processing(self))
			# otherwise we have to send task
		else:
			# elif self.destination.nodeType == constants.ELASTIC_NODE:
			print ("offloading to other device")
			print (self.processor)
			self.creator.addTask(subtask.createMessage(self))
			# subtask.communication(self.host, self.rawMessageSize()))

	def setProcessor(self, processingNode):
		print ("\tprocessor", self.hardwareAccelerated)
		if self.hardwareAccelerated:
			self.processor = processingNode.fpga
		else:
			self.processor = processingNode.mcu

	def offloaded(self):
		return self.creator is not self.processingNode

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
		return self.samples * constants.SAMPLE_RAW_SIZE.gen()

	def processedMessageSize(self):
		return self.samples * constants.SAMPLE_PROCESSED_SIZE.gen()


	# # change message from raw to processed
	# def process(self):
	# 	# if self.samples is None:
	# 	# 	warn("Cannot process message without sample count")
	# 	# self.size = self.samples * constants.SAMPLE_PROCESSED_SIZE.gen()