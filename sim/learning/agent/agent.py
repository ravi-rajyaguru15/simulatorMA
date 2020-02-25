import random

import numpy as np

import sim
from sim import debug, counters
from sim.learning.action import offloading, LOCAL, BATCH, action, OFFLOADING
# from sim.offloading import offloadingDecision
from sim.offloading.offloadingPolicy import LOCAL_ONLY, REINFORCEMENT_LEARNING, SPECIFIC_PEER_ONLY, RANDOM_PEER_ONLY, \
	ANNOUNCED, ANYTHING, ROUND_ROBIN
from sim.simulations import constants

class agent:
	sharedClock = None

	options = None
	target = None
	possibleActions = None  # TODO: offloading to self
	numOptions = None
	numActions = None
	metrics_names = None
	owner = None

	systemState = None
	model = None
	trainable_model = None
	policy = None
	loss = None
	# beforeState = None
	# latestAction = None
	latestLoss = None
	latestReward = None
	latestR = None
	latestMAE = None
	latestMeanQ = None
	gamma = None
	history = None

	device = None
	devices = None
	actionIndex = None

	totalReward = None
	episodeReward = None

	def __init__(self, systemState, owner=None):
		self.systemState = systemState
		self.owner = owner # owner none means shared

		self.totalReward = 0
		self.reset()

	def __repr__(self): return "<" + self.__name__ + ">"
		# self.setDevices(devices)

	def reset(self):
		self.episodeReward = 0

	# def setOptions(self, allDevices):
	# 	self.options = allDevices

	# def setOffloadingOptions(self, otherDevices):

	def setDevices(self, devices):
		# default devices is all of them
		# self.possibleActions = [offloading(i) for i in range(len(devices))] + [BATCH, LOCAL]
		self.possibleActions = [OFFLOADING, BATCH, LOCAL]
		self._setDecisions(devices)

	def getAction(self, action):
		return self.possibleActions[self.possibleActions.index(action)]

	def _setDecisions(self, devices):
		for i in range(len(self.possibleActions)):
			self.possibleActions[i].index = i
		print('actions', self.possibleActions)

		# self.numOptions = len(self.possibleActions)
		self.numActions = len(self.possibleActions)

		# needs numActions
		self.createModel()

		self.devices = devices

	def createModel(self):
		pass

	# self.history = sim.history.history()
	# def setDevices(self, devices):
	# 	raise self.genericException
	# def setDevices(self, devices):
	# 	assert devices is not None
	# 	self.possibleActions = [offloading(i) for i in range(len(devices))] + [BATCH, LOCAL]
	# 	for i in range(len(self.possibleActions)):
	# 		self.possibleActions[i].index = i
	# 	print('actions', self.possibleActions)
	# 	offloadingDecision.numActionsPerDevice = len(self.possibleActions)
	#
	# 	self.numActions = len(self.possibleActions)
	#
	# 	# needs numActions
	# 	self.createModel()
	#
	# 	self.devices = devices
	# 	# return self.possibleActions

	def chooseDestination(self, task, job, device):
		# default behaviour is to choose a random option
		if len(self.options) == 1:
			debug.out("only one option for job", 'y')
			choice = self.possibleActions[0]
			choice.updateTargetDevice(device, self.options)
		else:
			debug.out("assigning job randomly", 'y')
			choice = action("Random", targetIndex=random.choice(self.options).index)
			choice.updateTargetDevice(self.owner, self.options)
		return choice

		# # if specified fixed target, return it
		# if self.target is not None:
		# 	print("constant target")
		# 	return self.target  # possibleActions[self.target.index]
		# # check if shared target exists
		# elif agent.target is not None:
		# 	print("shared target")
		# 	return agent.target  # possibleActions[offloadingDecision.target.index]
		# elif self.options is None:
		# 	raise Exception("options are None!")
		# elif len(self.options) == 0:
		# 	raise Exception("No options available!")
		# else:
		# 	# choose randomly from the options available
		# 	if constants.OFFLOADING_POLICY == ANNOUNCED:
		# 		# every other offloading policy involves randoming
		# 		batches = np.array([len(dev.batch[task]) if task in dev.batch.keys() else 0 for dev in self.options])
		# 		# is the config already available?
		# 		configsAvailable = np.array([dev.fpga.currentConfig == task for dev in self.options])
		#
		# 		decisionFactors = batches + configsAvailable
		#
		# 		# nobody has a batch going
		# 		if np.sum(decisionFactors) == 0:
		# 			# then have to do it yourself
		# 			choice = action.findAction(self.owner.index)
		# 		else:
		# 			raise Exception("arguments incorrect")
		# 			largestBatches = np.argmax(decisionFactors)
		# 			# print('largest:', largestBatches)
		# 			choice = actionFromIndex(self.options[largestBatches].index)
		# 	elif constants.OFFLOADING_POLICY == LOCAL_ONLY:
		# 		choice = LOCAL
		# 		choice.updateTargetDevice(self.owner, [self.owner])
		# 	# choice = np.random.choice(self.options) #  action.findAction(random.choice(self.options).index)
		#
		# 	sim.debug.out("Job assigned: {} -> {}".format(self.owner, choice))
		# 	# if self.privateAgent is not None:
		# 	# 	choice.updateDevice() # self.privateAgent.devices)
		# 	# else:
		# 	# 	choice.updateDevice() # self.options)
		# 	return choice

	# # convert decision to a specific action
	# @staticmethod
	# def decodeIndex(index, options):
	# 	# deviceIndex = int(index / numActionsPerDevice)
	# 	# actionIndex = index - deviceIndex * numActionsPerDevice
	# 	# sim.debug.out(index, options)
	# 	# result = decision(options[deviceIndex], action=possibleActions[actionIndex])
	# 	# result = decision(options)
	# 	return result

	# def updateState(self, task, job, device):
	# 	# update state
	# 	self.systemState.

	genericException = Exception("Not implemented in generic agent")
	def train(self, task, job, device):
		raise self.genericException

	@staticmethod
	def selectElasticNodes(devices):
		return [node for node in devices if node.hasFpga()]


		# print("created shared", offloadingDecision.sharedAgent)
		# sim.learning.offloadingDecision.sharedAgent = agentClass(state)

	# def setOptions(self, allDevices):
	# 	raise self.genericException
		# # set options for all policies that use it, or select constant target
		# # if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.LOCAL_ONLY:
		# # 	self.target = self.owner
		# if constants.OFFLOADING_POLICY == RANDOM_PEER_ONLY:
		# 	# only offload to something with fpga when needed
		# 	elasticNodes = agent.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
		# 	if self.owner in elasticNodes:
		# 		elasticNodes.remove(self.owner)
		# 	self.options = elasticNodes
		# elif constants.OFFLOADING_POLICY == SPECIFIC_PEER_ONLY:
		# 	self.target = allDevices[constants.OFFLOADING_PEER]
		# elif constants.OFFLOADING_POLICY == ANYTHING \
		# 		or constants.OFFLOADING_POLICY == ANNOUNCED \
		# 		or constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING:
		# 	self.options = agent.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
		# # self.target = self.owner
		# elif constants.OFFLOADING_POLICY == ROUND_ROBIN:
		# 	# assign static targets (will happen multiple times but that's fine)
		# 	offloadingDecision.options = agent.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
		# # elif constants.OFFLOADING_POLICY == LOCAL_ONLY:
		# # 	offloadingDecision.options = [self.owner]
		# else:
		# 	raise Exception("Unknown offloading policy")
		#
		# # # setup learning if needed
		# # if constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING:
		# # 	# create either private or shared agent
		# # 	if not constants.CENTRALISED_LEARNING:
		# # 		self.agent = self.agentClass(self.systemState, allDevices)
		# # 	else:
		# # 		# create shared agent if required
		# # 		assert offloadingDecision.sharedAgent is not None
		# # 		self.agent = offloadingDecision.sharedAgent

	# default behaviour is just random choice
	def selectAction(self, systemState):
		action = np.random.randint(0, self.numOptions - 1)
		return action

	# predict best action using values
	def forward(self, task, job, device):
		self.systemState.updateState(task, job, device)

		debug.learnOut("forward", 'y')

		counters.NUM_FORWARD += 1

		currentSim = sim.simulations.Simulation.currentSimulation
		job.beforeState = self.systemState.fromSystemState(currentSim)
		sim.debug.out("beforestate {}".format(job.beforeState))
		# print(device.batchLengths(), device.batchLength(task), device.isQueueFull(task))

		# special case if job queue is full
		if device.isQueueFull(task):
			actionIndex = self.numActions - 1
			debug.learnOut("special case! queue is full")
		# check if any offloading is available
		elif not device.hasOffloadingOptions():
			assert self.possibleActions[0] is OFFLOADING
			debug.out("no offloading available")
			actionIndex = np.random.randint(1, self.numActions - 1)
		else:
			debug.out("getting action %s %s" % (device, device.batchLengths()))
			# choose best action based on current state
			actionIndex = self.selectAction(job.beforeState)
			# qValues = self.predict(job.beforeState)
			# actionIndex = self.selectAction(qValues)
		job.latestAction = actionIndex
		job.history.add("action", actionIndex)

		assert self.possibleActions is not None
		choice = self.possibleActions[actionIndex]
		sim.debug.learnOut("choice: {} ({})".format(choice, actionIndex), 'r')

		choice.updateTargetDevice(owner=device, offloadingDevices=device.offloadingOptions)
		# choice.updateTargetDevice(devices=self.devices)
		return choice

	# only used when using static target
	def updateOffloadingTarget(self):
		pass

	# check offloading decision on idle job
	def rechooseDestination(self, task, job, device):
		raise Exception("deprecated")
		# self.updateState(task, job, device)
		# self.privateAgent.backward(job.reward(), sim.simulations.current.finished)
		self.train(task, job, device)
		# choice = self.decideDestination(task, job, device)
		choice = self.forward(task, job, device)

		job.setDecisionTarget(choice)
		return job.activate()

		# return choice

	# update decision to see if should be uploaded again
	def redecideDestination(self, task, job, device):
		# assert constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING
		# print("redeciding")
		self.train(task, job, device)
		decision = self.forward(task, job, device)
		debug.out("redecided decision: %s" % decision)
		return decision

	# decide initial decision for job
	def firstDecideDestination(self, task, job, device):
		decision = self.forward(task, job, device)
		debug.out("initial decision: %s" % decision)
		return decision


