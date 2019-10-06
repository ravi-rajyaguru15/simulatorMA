import sys
from warnings import warn

import sim.constants
import sim.debug
# from sim.result import result
import sim.results
import sim.subtask
import sim.history
import sim.systemState
import sim.offloadingDecision
import sim.offloadingPolicy
import traceback
# from node import node

class job:
	# static results queue
	jobResultsQueue = None
	episodeFinished = None

	datasize = None
	samples = None

	started = None
	active = None
	createdTime = None
	startTime = None
	deadlineTime = None
	startExpectedLifetime = None

	totalEnergyCost = None
	totalLatency = None
	devicesEnergyCost = None # track how much each device spends on this job

	# history for learning
	beforeState = None
	latestAction = None

	owner = None
	# simulation = None
	creator = None
	processingNode = None
	processor = None
	# decision = None
	immediate = None
	id = 0

	hardwareAccelerated = None

	finished = None

	processed = None
	taskGraph = None
	currentTask = None
	batchSize = None
	incrementCompletedJobs = None

	history = None

	def __init__(self, origin, samples, hardwareAccelerated, taskGraph=None):
		job.id += 1
		self.id = job.id

		self.creator = origin
		# self.simulation = origin.simulation

		assert sim.simulation.current is not None
		simulation = sim.simulation.current
		self.incrementCompletedJobs = simulation.incrementCompletedJobs
		self.systemLifetime = simulation.systemLifetime
		self.startExpectedLifetime = self.systemLifetime()
		self.currentTime = simulation.time
		self.createdTime = self.currentTime.current

		self.samples = samples
		self.hardwareAccelerated = hardwareAccelerated
		self.totalEnergyCost = 0
		self.totalLatency = 0
		self.devicesEnergyCost = dict()

		# self.finished = False
		self.started = False
		self.active = False
		self.processed = False
		self.finished = False
		if taskGraph is None:
			taskGraph = sim.constants.DEFAULT_TASK_GRAPH
		self.taskGraph = taskGraph

		# start at first task
		self.currentTask = self.taskGraph[0]
		self.deadlineTime = self.createdTime + self.currentTask.deadline.gen()
		# initialise message size to raw data
		self.datasize = self.rawMessageSize()

		# private history to be used by rl
		self.history = sim.history.history()

		# initiate task by setting processing node
		self.setDecisionTarget(origin.decision.chooseDestination(self.currentTask, self, origin))

		# define episode finished function for training
		self.episodeFinished = simulation.isEpisodeFinished

	def __repr__(self):
		return "Job #{}".format(self.id)

	def setDecisionTarget(self, decision):
		# initiate task by setting processing node
		# decision.updateDevice()
		self.immediate = decision == sim.offloadingDecision.LOCAL
		sim.debug.out("set immediate to {}".format(self.immediate))

		# self.decision = decision
		assert decision.targetDevice is not None
		assert decision.targetDevice.index == decision.targetDeviceIndex
		# add to history
		assert self.history is not None

		# selectedDevice = self.simulation.devices[self.decision.targetDeviceIndex]
		sim.debug.out("selected {}".format(decision.targetDevice))
		self.setprocessingNode(decision.targetDevice)
		sim.results.addChosenDestination(decision.targetDevice)

		# when assigning a new target we can assume the job is inactive
		self.active = False


	def deadlineMet(self):
		return self.deadlineTime > self.currentTime

	def setprocessingNode(self, processingNode):
		self.processingNode = processingNode

		# sim.debug.out("setprocessingnode")

		self.setProcessor(processingNode)

	def setProcessor(self, processingNode):
		# sim.debug.out("\tprocessor " + str(self.hardwareAccelerated))
		if self.hardwareAccelerated:
			self.processor = processingNode.fpga
		else:
			self.processor = processingNode.mcu

	def reward(self):
		jobReward = 1 if self.finished else 0
		deadlineReward = 0 if self.deadlineMet() else -0.5
		expectedLifetimeReward = -.5 if (self.startExpectedLifetime > self.systemLifetime()) else 0

		sim.debug.learnOut('reward: {} {} {}'.format(jobReward, deadlineReward, expectedLifetimeReward), 'b')
		# traceback.print_stack()
		print('\n\n')

		return jobReward + deadlineReward + expectedLifetimeReward

	def addToHistory(self, reward, q, loss):
		self.history.add("reward", reward)
		self.history.add("q", q)
		self.history.add("loss", loss)

	def start(self):
		self.started = True
		self.startTime = self.currentTime.current

		# to start with, owner is the node who created it
		self.owner = self.creator

		self.activate()


	def activate(self):
		assert self.immediate is not None
		print("activating", self, 'owner', self.owner, 'on', self.processingNode)

		self.active = True

		# populate subtasks based on types of devices
		if not self.offloaded():
			print("already at correct place")
			if self.immediate:
				self.processingNode.addSubtask(sim.subtask.newJob(self))
			else:
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
			sim.debug.learnOut("training when finishing job")
			self.owner.decision.train(self.currentTask, self, self.owner)

			# agent = self.owner.decision.privateAgent
			# self.addToHistory(agent.latestReward, agent.latestMeanQ, agent.latestLoss)

		self.incrementCompletedJobs()

		# save this job's history to communal history
		if sim.results.learningHistory is None:
			sim.results.learningHistory = sim.history.history()
		sim.results.learningHistory.combine(self.history)

		# print("finished job", self.simulation.completedJobs)
		# add results to overall results
		# job.jobResultsQueue.put(self.totalLatency, self.totalEnergyCost))
		# print ("pushing", self.batchSize)
		# job.jobResultsQueue.put((self.currentTime - self.startTime,))
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
