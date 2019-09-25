import sys
from warnings import warn

import sim.constants
import sim.debug
# from sim.result import result
import sim.results
import sim.subtask

# from node import node

class job:
	# static results queue
	jobResultsQueue = None

	datasize = None
	samples = None
	
	started = None
	createdTime = None
	startTime = None
	deadlineTime = None
	startExpectedLifetime = None
	
	totalEnergyCost = None
	totalLatency = None
	devicesEnergyCost = None # track how much each device spends on this job
	
	owner = None
	simulation = None
	creator = None
	processingNode = None
	processor = None
	decision = None

	hardwareAccelerated = None

	finished = None

	processed = None
	taskGraph = None
	currentTask = None
	batchSize = None

	def __init__(self, createdTime, origin, samples, offloadingDecision, hardwareAccelerated, taskGraph=None):
		self.creator = origin
		self.simulation = origin.simulation

		self.startExpectedLifetime = self.simulation.systemLifetime()
		self.createdTime = createdTime

		self.samples = samples
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
		self.deadlineTime = createdTime + self.currentTask.deadline.gen()
		# initialise message size to raw data
		self.datasize = self.rawMessageSize()
		
		# initiate task by setting processing node
		self.applyDecision(offloadingDecision.chooseDestination(self.currentTask, self, self.simulation.time))
		
	def applyDecision(self, decision):
		# initiate task by setting processing node
		self.decision = decision
		selectedDevice = self.simulation.devices[self.decision.targetDeviceIndex]
		sim.debug.out("selected {}".format(selectedDevice))
		self.setprocessingNode(selectedDevice)
		sim.results.addChosenDestination(selectedDevice)
		

	def deadlineMet(self):
		return self.deadlineTime > self.simulation.time

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

	def reward(self):
		jobReward = 1 if self.finished else 0
		deadlineReward = 0 if self.deadlineMet() else -0.5
		expectedLifetimeReward = -.5 if (self.startExpectedLifetime > self.simulation.systemLifetime()) else 0

		return jobReward + deadlineReward + expectedLifetimeReward

	def start(self, startTime, batchSize=None):
		self.started = True
		self.startTime = startTime
		
		# to start with, owner is the node who created it 
		self.owner = self.creator

		self.activate(batchSize)
		

	def activate(self, batchSize=None):
		self.batchSize = batchSize if batchSize is not None else 0
		print("batch job:", self.batchSize)

		# populate subtasks based on types of devices
		if not self.offloaded():
			self.processingNode.addSubtask(sim.subtask.batching(self))
		# otherwise we have to send task
		else:
			# elif self.destination.nodeType == sim.constants.ELASTIC_NODE:
			sim.debug.out("offloading to other device")
			self.owner.addSubtask(sim.subtask.createMessage(self))
		

	def finish(self):
		self.finished = True
		self.owner.removeJob(self)

		if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.REINFORCEMENT_LEARNING:
			sim.systemState.current.updateJob(self, sim.systemState.current.currentTime)
			sim.systemState.current.updateTask(self.currentTask)
			sim.systemState.current.updateDevice(self.owner)
			agent = self.owner.decision.learningAgent
			agent.backward(self.reward(), self.finished)

		self.simulation.completedJobs += 1

		# print("finished job", self.simulation.completedJobs)
		# add results to overall results
		# job.jobResultsQueue.put(self.totalLatency, self.totalEnergyCost))
		print ("pushing", self.batchSize)
		job.jobResultsQueue.put((self.batchSize,))
		

	def offloaded(self):
		# in the beginning owner is creator, later may be offloaded again
		return self.owner is not self.processingNode

	def moveTo(self, destinationNode):
		# remove job from current
		currentOwner = self.owner
		sim.debug.out("current owner {}".format(currentOwner))
		currentOwner.removeJob(self) 

		sim.debug.out("moving from {} to {}".format(currentOwner, destinationNode))

		# set destination job
		if destinationNode.currentJob is None:
			destinationNode.currentJob = self
		else:
			sim.debug.out("ADDING JOB BECAUSE ALREADY HAS ONE")
			destinationNode.addJob(self)

		# add job to new owner
		# destinationNode.jobQueue.append(self)
		self.owner = destinationNode

	# def computeResult(self):
	# 	output = result()

	# 	for sub in self.subtasks:
	# 		output += result(latency=sub.totalDuration, energy=sub.energyCost)

	# 	return output

	def rawMessageSize(self):
		return self.samples * self.currentTask.rawSize

	def processedMessageSize(self):
		return self.samples * self.currentTask.processedSize
