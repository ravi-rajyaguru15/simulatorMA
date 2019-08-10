from warnings import warn

import sim.debug
import sim.constants 
import sim.subtask
from sim.result import result
# from node import node

class job:
	# static results queue
	jobResultsQueue = None

	datasize = None
	samples = None
	
	started = None
	createdTime = None
	startTime = None
	
	totalEnergyCost = None
	totalLatency = None
	devicesEnergyCost = None # track how much each device spends on this job
	
	owner = None
	creator = None
	processingNode = None
	processor = None

	hardwareAccelerated = None

	finished = None

	processed = None
	taskGraph = None
	currentTask = None

	def __init__(self, createdTime, origin, samples, offloadingDecision, hardwareAccelerated, taskGraph=None):
		self.creator = origin
		self.samples = samples
		# initialise message size to raw data
		self.datasize = self.rawMessageSize()
		self.hardwareAccelerated = hardwareAccelerated
		self.totalEnergyCost = 0
		self.totalLatency = 0
		self.devicesEnergyCost = dict()
		
		# self.finished = False
		self.started = False
		self.processed = False
		self.finished = False
		if taskGraph is None:
			taskGraph = sim.constants.DEFAULT_TASK_GRAPH
		self.taskGraph = taskGraph

		# start at first task
		self.currentTask = self.taskGraph[0]
		# initiate task by setting processing node
		self.setprocessingNode(offloadingDecision.chooseDestination(self))

	def setprocessingNode(self, processingNode):
		self.processingNode = processingNode

		sim.debug.out("setprocessingnode")

		self.setProcessor(processingNode)

	def setProcessor(self, processingNode):
		sim.debug.out("\tprocessor " + str(self.hardwareAccelerated))
		if self.hardwareAccelerated:
			self.processor = processingNode.fpga
		else:
			self.processor = processingNode.mcu


	def start(self, startTime):
		self.started = True
		self.startTime = startTime

		# populate subtasks based on types of devices
		if not self.offloaded():
			self.processingNode.addTask(sim.subtask.batching(self))
			# # local processing
			# if self.hardwareAccelerated:
			# 	# check if fpga already configured
			# 	if self.processingNode.fpga.isConfigured(self.currentTask):
			# 		self.processingNode.addTask(sim.subtask.mcuFpgaOffload(self))
			# 	else:
			# 		self.processingNode.addTask(sim.subtask.reconfigureFPGA(self))
			# else:
			# 	self.creator.addTask(sim.subtask.processing(self))
		# otherwise we have to send task
		else:
			# elif self.destination.nodeType == sim.constants.ELASTIC_NODE:
			sim.debug.out("offloading to other device")
			self.creator.addTask(sim.subtask.createMessage(self))
			# sim.subtask.communication(self.host, self.rawMessageSize()))

		# to start with, owner is the node who created it 
		self.owner = self.creator

	def finish(self):
		self.finished = True
		self.owner.removeJob(self)

		# add results to overall results
		job.jobResultsQueue.put(result(self.totalLatency, self.totalEnergyCost))

		# see if there's a next job to continue
		self.processingNode.addTask(sim.subtask.batchContinue(self))
		

	def offloaded(self):
		return self.creator is not self.processingNode

	def process(self):
		print ("PANIC")
		# figure out which sim.subtask is active
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
						nextSubTask.destination.addSubTask(sim.subtask.communication())
						nextSubTask.destination.addSubTask(sim.subtask.communication())
						nextSubTask.destination.addSubTask(sim.subtask.communication())
						# nextSubTask.destination.prependTask(sim.subtask.communication())

				if destinationReady:
					self.currentSubTask = nextSubTask

		# progress sim.subtask 
		self.currentSubTask.tick()

		if self.currentSubTask.finished:
			self.subtaskIndex += 1
			self.currentSubTask = None

	def moveTo(self, destinationNode):
		# remove job from current
		currentOwner = self.owner
		currentOwner.removeJob(self)

		sim.debug.out("moving from {} to {}".format(currentOwner, destinationNode))


		# add job to new owner
		# destinationNode.jobQueue.append(self)
		self.owner = destinationNode

	# def computeResult(self):
	# 	output = result()

	# 	for sub in self.subtasks:
	# 		output += result(latency=sub.totalDuration, energy=sub.energyCost)

	# 	return output

	def rawMessageSize(self):
		return self.samples * sim.constants.SAMPLE_RAW_SIZE.gen()

	def processedMessageSize(self):
		return self.samples * sim.constants.SAMPLE_PROCESSED_SIZE.gen()


	# # change message from raw to processed
	# def process(self):
	# 	# if self.samples is None:
	# 	# 	warn("Cannot process message without sample count")
	# 	# self.size = self.samples * sim.constants.SAMPLE_PROCESSED_SIZE.gen()
