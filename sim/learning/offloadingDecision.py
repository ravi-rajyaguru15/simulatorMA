import random

import numpy as np
import rl
import rl.policy
import rl.util
import tensorflow as tf
import tensorflow.keras as keras

import sim.simulations
import sim.learning.systemState
import sim.counters
import sim.debug
import sim.offloading.offloadingPolicy
from sim.offloading.offloadingPolicy import *
from sim.simulations import constants

sharedAgent = None
possibleActions = None  # TODO: offloading to self
devices = None
sharedClock = None


class offloadingDecision:
	options = None
	owner = None
	target = None
	simulation = None
	privateAgent = None

	def __init__(self, device, systemState):
		self.owner = device
		self.systemState = systemState

	@staticmethod
	def selectElasticNodes(devices):
		return [node for node in devices if node.hasFpga()]

	def setOptions(self, allDevices):
		# set options for all policies that use it, or select constant target
		# if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.LOCAL_ONLY:
		# 	self.target = self.owner
		if constants.OFFLOADING_POLICY == RANDOM_PEER_ONLY:
			# only offload to something with fpga when needed
			elasticNodes = offloadingDecision.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
			if self.owner in elasticNodes:
				elasticNodes.remove(self.owner)
			self.options = elasticNodes
		elif constants.OFFLOADING_POLICY == SPECIFIC_PEER_ONLY:
			self.target = allDevices[constants.OFFLOADING_PEER]
		elif constants.OFFLOADING_POLICY == ANYTHING \
				or constants.OFFLOADING_POLICY == ANNOUNCED \
				or constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING:
			self.options = offloadingDecision.selectElasticNodes(
				allDevices)  # select elastic nodes from alldevices list]
		# self.target = self.owner
		elif constants.OFFLOADING_POLICY == ROUND_ROBIN:
			# assign static targets (will happen multiple times but that's fine)
			offloadingDecision.options = offloadingDecision.selectElasticNodes(
				allDevices)  # select elastic nodes from alldevices list]
		elif constants.OFFLOADING_POLICY == LOCAL_ONLY:
			offloadingDecision.options = [self.owner]
		else:
			raise Exception("Unknown offloading policy")

		# setup learning if needed
		if constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING:
			# create either private or shared agent
			if not constants.CENTRALISED_LEARNING:
				self.privateAgent = agent(self.systemState)
			else:
				# create shared agent if required
				assert sharedAgent is not None
				self.privateAgent = sharedAgent

	# print(sim.constants.OFFLOADING_POLICY, self.owner, self.options)

	def chooseDestination(self, task, job, device):
		# if specified fixed target, return it
		if self.target is not None:
			print("constant target")
			return self.target  # possibleActions[self.target.index]
		# check if shared target exists
		elif offloadingDecision.target is not None:
			print("shared target")
			return offloadingDecision.target  # possibleActions[offloadingDecision.target.index]
		elif self.options is None:
			raise Exception("options are None!")
		elif len(self.options) == 0:
			raise Exception("No options available!")
		else:
			# choose randomly from the options available
			if constants.OFFLOADING_POLICY == ANNOUNCED:
				# every other offloading policy involves randoming
				batches = np.array([len(dev.batch[task]) if task in dev.batch.keys() else 0 for dev in self.options])
				# is the config already available?
				configsAvailable = np.array([dev.fpga.currentConfig == task for dev in self.options])

				decisionFactors = batches + configsAvailable

				# nobody has a batch going
				if np.sum(decisionFactors) == 0:
					# then have to do it yourself
					choice = action.findAction(self.owner.index)
				else:
					largestBatches = np.argmax(decisionFactors)
					# print('largest:', largestBatches)
					choice = action.findAction(self.options[largestBatches].index)
			elif constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING:
				sim.debug.learnOut("deciding how to offload new job")
				sim.debug.learnOut("owner: {}".format(self.owner), 'r')
				choice = self.firstDecideDestination(task, job, device)
			# sim.debug.learnOut("choice: {}".format(choice))
			elif constants.OFFLOADING_POLICY == LOCAL_ONLY:
				choice = sim.learning.offloadingDecision.LOCAL
				choice.updateDevice(self.owner)
			else:
				choice = action("Random", targetIndex=random.choice(self.options).index)
				choice.updateDevice(self.owner)
			# choice = np.random.choice(self.options) #  action.findAction(random.choice(self.options).index)

			sim.debug.out("Job assigned: {} -> {}".format(self.owner, choice))
			# if self.privateAgent is not None:
			# 	choice.updateDevice() # self.privateAgent.devices)
			# else:
			# 	choice.updateDevice() # self.options)
			return choice

	def rechooseDestination(self, task, job, device):
		# self.updateState(task, job, device)
		# self.privateAgent.backward(job.reward(), sim.simulations.current.finished)
		self.train(task, job, device)
		# choice = self.decideDestination(task, job, device)
		choice = self.privateAgent.forward(job, device)

		job.setDecisionTarget(choice)
		# job.activate()

		return choice

	def redecideDestination(self, task, job, device):
		assert constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING
		# print("redeciding")
		self.train(task, job, device)
		return self.privateAgent.forward(job, device)

	def firstDecideDestination(self, task, job, device):
		self.updateState(task, job, device)
		return self.privateAgent.forward(job, device)

	def updateState(self, task, job, device):
		# update state
		self.systemState.update(task, job, device)

	def train(self, task, job, device):
		sim.debug.learnOut("Training: [{}] [{}] [{}]".format(task, job, device), 'y')
		self.updateState(task, job, device)
		self.privateAgent.backward(job)


# print("choice: {}".format(choice))

previousUpdateTime = None
currentTargetIndex = -1


# @staticmethod
def updateOffloadingTarget():
	assert sharedClock is not None

	newTarget = False
	# decide if 
	if offloadingDecision.previousUpdateTime is None:
		sim.debug.out("first round robin")
		# start at the beginning
		offloadingDecision.currentTargetIndex = 0
		newTarget = True
	elif sharedClock >= (offloadingDecision.previousUpdateTime + constants.ROUND_ROBIN_TIMEOUT):
		# print ("next round robin")
		offloadingDecision.currentTargetIndex += 1
		if offloadingDecision.currentTargetIndex >= len(offloadingDecision.options):
			# start from beginning again
			offloadingDecision.currentTargetIndex = 0
		newTarget = True

	# new target has been chosen:
	if newTarget:
		# indicate to old target to process batch immediately
		if offloadingDecision.target is not None:
			sim.debug.out("offloading target", offloadingDecision.target.offloadingDecision)
			# time.sleep(1)
			offloadingDecision.target.addSubtask(sim.subtask.batchContinue(node=offloadingDecision.target))

		offloadingDecision.previousUpdateTime = sharedClock.current
		offloadingDecision.target = offloadingDecision.options[offloadingDecision.currentTargetIndex]

		sim.debug.out("Round robin update: {}".format(offloadingDecision.target), 'r')


def mean_q(correctQ, predictedQ):
	return tf.keras.backend.mean(tf.keras.backend.max(predictedQ, axis=-1))


class action:
	name = None
	targetDevice = None
	targetDeviceIndex = None
	local = False
	# index = None
	immediate = None

	def __init__(self, name, targetIndex=None, immediate=False):
		if targetIndex is None:
			self.name = name
			self.local = True
		else:
			self.name = "{} {}".format(name, targetIndex)
			self.targetDeviceIndex = targetIndex
			self.local = False
		self.immediate = immediate

	def __repr__(self):
		return self.name

	def offloadingToTarget(self, targetIndex=None): return False

	# update device based on latest picked device index
	def updateDevice(self, owner=None):
		if self.local:
			assert owner is not None
			self.targetDeviceIndex = owner.index
			self.targetDevice = owner
		else:
			assert self.targetDeviceIndex is not None
			assert devices is not None

			self.targetDevice = None
			# find device based on its index
			for device in devices:
				if device.index == self.targetDeviceIndex:
					self.targetDevice = device
					break

			if self.targetDevice is None:
				print("updateDevice failed!", self, devices, self.targetDeviceIndex)

			assert self.targetDevice is not None
	# self.targetDevice = devices[self.targetDeviceIndex]

# def setTargetDevice(self, device):
# 	self.targetDevice = device


class offloading(action):
	def __init__(self, destinationIndex):
		super().__init__("Offload", targetIndex=destinationIndex)

	def offloadingToTarget(self, index):
		return self.targetDeviceIndex == index


class localAction(action):
	def __init__(self, immediate):
		if immediate:
			name = "Local"
		else:
			name = "Batch"
		super().__init__(name, immediate=immediate)


BATCH = localAction(False)  # TODO: wait does nothing
LOCAL = localAction(True)


# OFFLOAD = action("Offload")


class agent:
	systemState = None
	dqn = None
	model = None
	trainable_model = None
	policy = None
	optimizer = None
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

	@property
	def metrics_names(self):
		# Throw away individual losses and replace output name since this is hidden from the user.
		assert len(self.trainable_model.output_names) == 2
		dummy_output_name = self.trainable_model.output_names[1]
		model_metrics = [name for idx, name in enumerate(self.trainable_model.metrics_names) if idx not in (1, 2)]
		model_metrics = [name.replace(dummy_output_name + '_', '') for name in model_metrics]

		names = model_metrics + self.policy.metrics_names[:]

		return names

	def __init__(self, systemState):
		self.systemState = systemState

		self.gamma = constants.GAMMA

		sim.debug.out(constants.OFFLOADING_POLICY)
		self.policy = rl.policy.EpsGreedyQPolicy(eps=constants.EPS)
		# self.dqn = rl.agents.DQNAgent(model=self.model, policy=rl.policy.LinearAnnealedPolicy(, attr='eps', value_max=sim.constants.EPS_MAX, value_min=sim.constants.EPS_MIN, value_test=.05, nb_steps=sim.constants.EPS_STEP_COUNT), enable_double_dqn=False, gamma=.99, batch_size=1, nb_actions=self.numActions)
		self.optimizer = keras.optimizers.Adam(lr=constants.LEARNING_RATE)

		self.totalReward = 0
		self.reset()

	# self.setDevices()

	def reset(self):
		self.episodeReward = 0

	# self.history = sim.history.history()

	def setDevices(self):
		# self.devices = devices
		# create actions
		global possibleActions
		global devices
		assert devices is not None
		possibleActions = [offloading(i) for i in range(len(devices))] + [BATCH, LOCAL]
		for i in range(len(possibleActions)):
			possibleActions[i].index = i
		print('actions', possibleActions)
		offloadingDecision.numActionsPerDevice = len(possibleActions)

		self.numActions = len(possibleActions)

		# needs numActions
		self.createModel()

	def createModel(self):
		# create basic model
		self.model = keras.models.Sequential()
		self.model.add(keras.layers.Flatten(input_shape=(1,) + (self.systemState.stateCount,)))
		# print('input shape', (1,) + env.observation_space.shape)
		self.model.add(keras.layers.Dense(4))
		self.model.add(keras.layers.Activation('relu'))
		# self.model.add(keras.layers.Dense(16))
		# self.model.add(keras.layers.Activation('relu'))

		self.model.add(keras.layers.Dense(self.numActions))
		self.model.add(keras.layers.Activation('linear'))
		# if sim.debug.enabled:
		# 	self.model.summary()

		self.createTrainableModel()

	def createTrainableModel(self):
		# COPIED FROM KERAS-RL LIBRARY
		metrics = ['mae']
		metrics += [mean_q]  # register default metrics

		def clipped_masked_error(args):
			correctQ, predictedQ, mask = args
			loss = rl.util.huber_loss(correctQ, predictedQ, np.inf)
			loss *= mask  # apply element-wise mask
			return tf.keras.backend.sum(loss, axis=-1)

		# Create trainable model. The problem is that we need to mask the output since we only
		# ever want to update the Q values for a certain action. The way we achieve this is by
		# using a custom Lambda layer that computes the loss. This gives us the necessary flexibility
		# to mask out certain parameters by passing in multiple inputs to the Lambda layer.
		predictedQ = self.model.output
		correctQ = keras.layers.Input(name='correctQ', shape=(self.numActions,))
		mask = keras.layers.Input(name='mask', shape=(self.numActions,))
		lossOut = keras.layers.Lambda(clipped_masked_error, output_shape=(1,), name='loss')(
			[correctQ, predictedQ, mask])
		# this copies the existing model
		ins = [self.model.input] if type(self.model.input) is not list else self.model.input
		self.trainable_model = keras.models.Model(inputs=ins + [correctQ, mask], outputs=[lossOut, predictedQ])
		assert len(self.trainable_model.output_names) == 2
		combined_metrics = {self.trainable_model.output_names[1]: metrics}
		losses = [
			lambda correctQ, predictedQ: predictedQ,  # loss is computed in Lambda layer
			lambda correctQ, predictedQ: tf.keras.backend.zeros_like(predictedQ),
			# we only include this for the metrics
		]
		self.trainable_model.compile(optimizer=self.optimizer, loss=losses, metrics=combined_metrics)

	# # convert decision to a specific action 
	# @staticmethod
	# def decodeIndex(index, options):
	# 	# deviceIndex = int(index / numActionsPerDevice)
	# 	# actionIndex = index - deviceIndex * numActionsPerDevice
	# 	# sim.debug.out(index, options)
	# 	# result = decision(options[deviceIndex], action=possibleActions[actionIndex])
	# 	# result = decision(options)
	# 	return result

	# predict best action using Q values
	def forward(self, job, device):
		sim.debug.learnOut("forward", 'y')
		assert self.model is not None

		sim.counters.NUM_FORWARD += 1

		job.beforeState = sim.learning.systemState.systemState.fromSystemState(sim.learning.systemState.current, sim.simulations.current)
		sim.debug.out("beforestate {}".format(job.beforeState))
		qValues = self.model.predict(job.beforeState.currentState.reshape((1, 1, self.systemState.stateCount)))[0]
		# sim.debug.learnOut('q {}'.format(qValues))
		actionIndex = self.policy.select_action(q_values=qValues)
		job.latestAction = actionIndex
		job.history.add("action", actionIndex)
		# sim.debug.learnOut("chose action {}".format(actionIndex))
		# self.history["action"].append(float(self.latestAction))

		assert sim.learning.offloadingDecision.possibleActions is not None
		choice = sim.learning.offloadingDecision.possibleActions[actionIndex]
		sim.debug.learnOut("choice: {} ({})".format(choice, actionIndex), 'r')

		choice.updateDevice(device)
		return choice

	# update based on resulting system state and reward
	def backward(self, job):
		assert self.trainable_model is not None

		reward = job.reward()
		finished = job.episodeFinished()

		sim.debug.learnOut("backward {} {}".format(reward, finished), 'y')
		sim.debug.learnOut("\n")
		# traceback.print_stack()
		# sim.debug.learnOut("\n")

		self.totalReward += reward
		self.episodeReward += reward

		sim.counters.NUM_BACKWARD += 1

		metrics = [np.nan for _ in self.metrics_names]

		# Compute the q_values given state1, and extract the maximum for each sample in the batch.
		# We perform this prediction on the target_model instead of the model for reasons
		# outlined in Mnih (2015). In short: it makes the algorithm more stable.
		target_q_values = self.model.predict_on_batch(
			np.array([np.array([np.array(sim.learning.systemState.current.currentState)])]))  # TODO: target_model
		q_batch = np.max(target_q_values, axis=1).flatten()

		targets = np.zeros((1, self.numActions))
		dummy_targets = np.zeros((1,))
		masks = np.zeros((1, self.numActions))

		# Compute r_t + gamma * max_a Q(s_t+1, a) and update the target targets accordingly,
		# but only for the affected output units (as given by action_batch).
		discounted_reward_batch = self.gamma * q_batch
		# Set discounted reward to zero for all states that were terminal.
		discounted_reward_batch *= [0. if finished else 1.]
		# assert discounted_reward_batch.shape == reward_batch.shape
		R = reward + discounted_reward_batch
		targets[0, job.latestAction] = R  # update action with estimated accumulated reward
		dummy_targets[0] = R
		masks[0, job.latestAction] = 1.  # enable loss for this specific action

		targets = np.array(targets).astype('float32')
		masks = np.array(masks).astype('float32')

		# Finally, perform a single update on the entire batch. We use a dummy target since
		# the actual loss is computed in a Lambda layer that needs more complex input. However,
		# it is still useful to know the actual target to compute metrics properly.
		x = [np.array([[job.beforeState.currentState]])] + [targets, masks]
		y = [dummy_targets, targets]

		self.trainable_model._make_train_function()
		metrics = self.trainable_model.train_on_batch(x, y)
		# metrics = metrics[1:3]
		metrics = [metric for idx, metric in enumerate(metrics) if idx not in (1, 2)]  # throw away individual losses
		metrics += self.policy.metrics
		# print(metrics, self.metrics_names)

		# new metrics
		self.latestLoss = metrics[0]
		self.latestReward = reward
		self.latestR = R
		self.latestMAE = metrics[1]
		self.latestMeanQ = metrics[2]

		# sim.debug.learnOut\
		diff = sim.learning.systemState.current - job.beforeState
		np.set_printoptions(precision=3)
		sim.debug.infoOut("{}, created: {:6.3f} {:<7}: {}, deadline: {:9.5f} ({:10.5f}), action: {:<9}, expectedLife (before: {:9.5f} - after: {:9.5f}) = {:10.5f}, reward: {}".format(job.currentTime, job.createdTime, str(job), int(job.finished), job.deadlineRemaining(), (job.currentTime - job.createdTime), str(possibleActions[job.latestAction]), job.beforeState.	getField("selfExpectedLife")[0], sim.learning.systemState.current.getField("selfExpectedLife")[0], diff["selfExpectedLife"][0], reward))
		# print("state diff: {}".format(diff).replace("array", ""), 'p')

		# save to history
		job.addToHistory(self.latestReward, self.latestMeanQ, self.latestLoss)

		# # metrics history
		# self.history.add("loss", self.loss)
		# self.history["reward"].append(self.latestReward)
		# self.history["q"].append(self.latestMeanQ)

		# print('reward', reward)

		sim.debug.learnOut("loss: {} reward: {} R: {}".format(self.latestLoss, self.latestReward, self.latestR), 'r')

	# agent.step += 1
	# agent.update_target_model_hard()

	# return metrics

# @staticmethod
# def findAction(targetIndex):


def actionFromIndex(index):
	return sim.learning.offloadingDecision.possibleActions[index]

# def actionFromTarget(targetIndex):
# 	# find target device for offloading that matches this index
# 	targets = [device for action in possibleActions if action.targetDeviceIndex == targetIndex]
# 	assert len(targets) == 1
# 	return targets[0]
