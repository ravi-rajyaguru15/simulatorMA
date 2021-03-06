import random
import sys
from copy import deepcopy
from random import choice

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
	# numOptions = None
	numActions = None
	metrics_names = None
	owner = None

	systemState = None
	currentSystemState = None

	model = None
	trainable_model = None
	policy = None
	loss = None
	# beforeState = None
	latestAction = None
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
	productionMode = None
	offPolicy = None
	episodeNumber = None

	numChosenAction = dict()

	reconsiderBatches = None

	trainingData = None

	def __init__(self, systemState, reconsiderBatches, owner=None, offPolicy=constants.OFF_POLICY, trainClassification=None):
		self.systemState = systemState
		self.currentSystemState = systemState
		# print("set systemstate to", systemState)
		self.owner = owner  # owner none means shared

		self.offPolicy = offPolicy

		self.totalReward = 0
		self.productionMode = False
		self.reset(0)
		self.setReconsiderBatches(reconsiderBatches)

		self.trainingData = []

		# classification is irrelevant here

	def setReconsiderBatches(self, reconsiderBatches): self.reconsiderBatches = reconsiderBatches

	def __repr__(self): return "<" + self.__name__ + ">"

	def reset(self, episodeNumber):
		self.episodeReward = 0
		self.numChosenAction = dict()
		self.episodeNumber = episodeNumber

	def incrementChosenAction(self, action):
		if action in self.numChosenAction:
			self.numChosenAction[action] += 1
		else:
			self.numChosenAction[action] = 1

	def getChosenAction(self, action):
		if action in self.numChosenAction:
			return self.numChosenAction[action]
		else:
			return 0
	def setProductionMode(self, value=True):
		debug.learnOut("switching to production mode!", 'y')
		self.productionMode = value

	# def setOptions(self, allDevices):
	# 	self.options = allDevices

	# def setOffloadingOptions(self, otherDevices):

	def getOffloadingTargets(self, devices):
		return devices

	def setDevices(self, devices):
		if len(devices) == 1:
			# offloading impossible if only one device present
			self.possibleActions = [BATCH, LOCAL]
		else:
			# default devices is all of them
			# self.possibleActions = [offloading(i) for i in range(len(devices))] + [BATCH, LOCAL]
			self.possibleActions = [OFFLOADING, BATCH, LOCAL]
		self._setDecisions(devices)

	def getAction(self, action):
		if action is not None:
			if not (isinstance(action, int) or isinstance(action, np.int64)):
				index = self.getActionIndex(action)
			else:
				index = action
			return self.possibleActions[index]
		else:
			return None

	def getActionIndex(self, action):
		return self.possibleActions.index(action)

	def _setDecisions(self, devices):
		for i in range(len(self.possibleActions)):
			self.possibleActions[i].index = i
		debug.learnOut('actions %s' % self.possibleActions)

		# self.numOptions = len(self.possibleActions)
		self.numActions = len(self.possibleActions)

		# new model is created because it uses numActions
		# self.createModel()


		self.devices = devices

	def createModel(self):
		pass

	def updateTargetModel(self):
		raise self.genericException

	def updateModel(self):
		raise self.genericException


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
		if len(self.possibleActions) == 1:
			debug.out("only one option for job", 'y')
			# choice = self.possibleActions[0]
			decision = self.getAction(OFFLOADING)
		elif not device.hasOffloadingOptions():
			debug.out("only option is local")
			if self.possibleActions[0] is OFFLOADING:
			# assert self.possibleActions[0] is OFFLOADING
				decision = choice(self.possibleActions[1:])
			else:
				decision = choice(self.possibleActions)
		else:
			debug.out("assigning job randomly", 'y')
			# choice = action("Random", targetIndex=random.choice(self.options).index)
			decision = choice(self.possibleActions)
		decision.updateTargetDevice(device, device.offloadingOptions)
		return decision

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

	def getEpsilon(self):
		# calculate decaying epsilon for greedy-e
		if constants.EPS_DECAY:
			if self.episodeNumber < constants.EPS_STEP_COUNT:
				epsilon = constants.EPS * (1 - self.episodeNumber / constants.EPS_STEP_COUNT)
			else:
				epsilon = 0
		else:
			epsilon = constants.EPS
		# print(epsilon)
		return epsilon

	# default behaviour is just random choice
	def selectAction(self, systemState):
		action = random.randint(0, self.numActions - 1)
		return action

	# predict best action using values
	def forward(self, task, job, device):
		# self.systemState.updateState(task, job, device)

		# debug.learnOut("forward", 'y')

		counters.NUM_FORWARD += 1

		# currentSim = sim.simulations.Simulation.currentSimulation
		# job.beforeState = deepcopy(self.systemState)
		job.beforeState = self.systemState.getCurrentState(task, job, device)
		job.reset()

		sim.debug.out(debug.formatDebug("beforestate {}",job.beforeState))

		# if job.beforeState[0] == 4 and job.beforeState[1] == 0:
		# debug.learnOut("%s choosing for %s" % (device, job))

		# print(device.batchLengths(), device.batchLength(task), device.isQueueFull(task))

		# special case if job queue is full
		if device.isQueueFull(task):
			actionIndex = self.numActions - 1
			debug.learnOut(debug.formatLearn("\nSpecial case! %s queue is full %s %d %s %s", (job, device.batchLengths(), actionIndex, self.possibleActions[actionIndex], job.beforeState)), 'r')

			# print("queue full")
		# check if no offloading is available
		elif not device.hasOffloadingOptions() and OFFLOADING in self.possibleActions:
			# if self.possibleActions[0] is not OFFLOADING:
			# 	print(self.possibleActions)
			# debug.out(self.possibleActions)
			# if self.possibleActions[0] is OFFLOADING:
			# elif len(self.devices):
			# 	actionIndex = np.random.randint(0, )
			assert self.possibleActions[0] is OFFLOADING
			actionIndex = np.random.randint(1, self.numActions - 1)
			debug.out("no offloading available")
			# print("random")
		else:
			debug.out("getting action %s %s" % (device, device.batchLengths()))
			# choose best action based on current state
			actionIndex = self.selectAction(job.beforeState)
			debug.learnOut(debug.formatLearn("\nChoose %s for %s: %d %s %s", (device, job, actionIndex, self.possibleActions[actionIndex], job.beforeState)), 'g')
			# qValues = self.predict(job.beforeState)
			# actionIndex = self.selectAction(qValues)
			# print("chose")
		job.latestAction = actionIndex
		job.history.add("action", actionIndex)

		assert self.possibleActions is not None
		choice = self.possibleActions[actionIndex]
		# sim.debug.learnOut("choice: {} ({})".format(choice, actionIndex), 'r')

		choice.updateTargetDevice(owner=device, offloadingDevices=device.offloadingOptions)
		# choice.updateTargetDevice(devices=self.devices)

		self.incrementChosenAction(choice)

		return choice

	# only used when using static target
	def updateOffloadingTarget(self):
		pass

	# # check offloading decision on idle job
	# def rechooseDestination(self, task, job, device):
	# 	raise Exception("deprecated")
	# 	# self.updateState(task, job, device)
	# 	# self.privateAgent.backward(job.reward(), sim.simulations.current.finished)
	# 	self.train(task, job, device)
	# 	# choice = self.decideDestination(task, job, device)
	# 	choice = self.forward(task, job, device)
	#
	# 	job.setDecisionTarget(choice)
	# 	return job.activate()

		# return choice

	# update decision to see if should be uploaded again
	def redecideDestination(self, task, job, device):
		# assert constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING
		# print("redeciding")
		# self.train(task, job, device)
		decision = self.forward(task, job, device)
		debug.out("redecided decision: %s" % decision)
		return decision

	# decide initial decision for job
	def firstDecideDestination(self, task, job, device):
		decision = self.forward(task, job, device)
		debug.out("initial decision: %s" % decision)
		return decision


