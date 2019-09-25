import sim.constants
import sim.debug
import sim.offloadingPolicy
# import sim.elasticNode

# import matplotlib.pyplot as pp
# import matplotlib as mpl
# import matplotlib.image
# import warnings
# import random
# import time
import numpy as np
# import sys
# if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.REINFORCEMENT_LEARNING:
import rl
import rl.util
import rl.policy
# import rl.core.agent
import tensorflow as tf

import tensorflow.keras as keras
import tensorflow.keras.backend


class offloadingDecision:
	options = None
	owner = None
	target = None
	simulation = None
	learningAgent = None


	def __init__(self, device, systemState):
		self.owner = device
		self.systemState = systemState

		offloadingDecision.possibleActions = [action("Offload", i) for i in range(sim.constants.NUM_DEVICES)] + [BATCH, LOCAL]
		print('actions', offloadingDecision.possibleActions)
		offloadingDecision.numActionsPerDevice = len(offloadingDecision.possibleActions)



	@staticmethod
	def selectElasticNodes(devices):
		return [node for node in devices if node.hasFpga()]

	def setOptions(self, allDevices):
		# set options for all policies that use it, or select constant target
		if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.LOCAL_ONLY:
			self.target = self.owner
		elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.RANDOM_PEER_ONLY:
			# only offload to something with fpga when needed
			elasticNodes = offloadingDecision.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
			if self.owner in elasticNodes:
				elasticNodes.remove(self.owner)
			self.options = elasticNodes
		elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.SPECIFIC_PEER_ONLY:
			self.target = allDevices[sim.constants.OFFLOADING_PEER]
		elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.ANYTHING \
			or sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.ANNOUNCED \
			or sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.REINFORCEMENT_LEARNING:
			self.options = offloadingDecision.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
			# self.target = self.owner
		elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.ROUND_ROBIN:
			# assign static targets (will happen multiple times but that's fine)
			offloadingDecision.options = offloadingDecision.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
	
		else:
			raise Exception("Unknown offloading policy")

		# setup learning if needed
		if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.REINFORCEMENT_LEARNING:
			# create either private or shared agent
			if not sim.constants.CENTRALISED_LEARNING:
				self.learningAgent = agent(self.systemState)
			else:
				# create shared agent if required
				if offloadingDecision.learningAgent is None:
					offloadingDecision.learningAgent = agent(self.systemState)
				self.learningAgent = offloadingDecision.learningAgent

		# print(sim.constants.OFFLOADING_POLICY, self.owner, self.options)

	def chooseDestination(self, task, job, currentTime):
		# if specified fixed target, return it
		if self.target is not None:
			return offloadingDecision.possibleActions[self.target.index]
		# check if shared target exists
		elif offloadingDecision.target is not None:
			print ("shared target")
			return offloadingDecision.possibleActions[offloadingDecision.target.index]
		elif self.options is None:
			raise Exception("options are None!")
		elif len(self.options) == 0:
			raise Exception("No options available!")
		else:
			# choose randomly from the options available
			if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.ANNOUNCED:
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
			elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.REINFORCEMENT_LEARNING:
				print()
				print("deciding how to offload new job")
				print("owner:", self.owner)
				self.systemState.updateDevice(self.owner)
				self.systemState.updateJob(job, currentTime)
				self.systemState.updateTask(task)
				sim.debug.out("systemstate: {}".format(self.systemState))
				# print("systemstate: {}".format(self.systemState))
				choice = self.learningAgent.forward()
				sim.debug.out("choice: {}".format(choice))
				print("choice: {}".format(choice))
			else:
				choice = action.findAction(random.choice(self.options).index)

			sim.debug.out("Job assigned: {} -> {}".format(self.owner, choice))
			return choice
		

	previousUpdateTime = None
	currentTargetIndex = -1
	@staticmethod
	def updateOffloadingTarget(currentTime):
		newTarget = False
		# decide if 
		if offloadingDecision.previousUpdateTime is None:
			sim.debug.out("first round robin")
			# start at the beginning
			offloadingDecision.currentTargetIndex = 0
			newTarget = True
		elif currentTime >= (offloadingDecision.previousUpdateTime + sim.constants.ROUND_ROBIN_TIMEOUT):
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

			offloadingDecision.previousUpdateTime = currentTime
			offloadingDecision.target = offloadingDecision.options[offloadingDecision.currentTargetIndex]

			sim.debug.out("Round robin update: {}".format(offloadingDecision.target), 'r')





def mean_q(correctQ, predictedQ):
	return tf.keras.backend.mean(tf.keras.backend.max(predictedQ, axis=-1))
class action:
	name = None
	targetDeviceIndex = None
	local = False

	def __init__(self,name, targetIndex=None):
		if targetIndex is None:
			self.name = name
			self.local = True
		else:
			self.name = "{} {}".format(name, targetIndex)
			self.targetDeviceIndex = targetIndex
			self.local = False

	def __repr__(self): return self.name

	# @staticmethod
	# def findAction(targetIndex):
	# 	# find target device for offloading that matches this index
	# 	targets = [device for action in possibleActions if action.targetDeviceIndex == targetIndex]
	# 	assert len(targets) == 1
	# 	return targets[0]

BATCH = action("Batch") # TODO: wait does nothing
LOCAL = action("Local")
# OFFLOAD = action("Offload")

# TODO: offloading to self
possibleActions = None



# class decision:
# 	targetDevice = None
# 	targetAction = None

# 	def __init__(self, device, action):
# 		self.targetDevice = device
# 		self.targetAction = action

# 	def __repr__(self): 
# 		return "{} - {}".format(self.targetDevice, self.targetAction)

class agent:
	systemState = None
	dqn = None
	model = None
	trainable_model = None
	policy = None
	optimizer = None
	loss = None
	beforeState = None
	latestAction = None
	latestReward = None
	latestMAE = None
	latestMeanQ = None
	gamma = None


	@property
	def metrics_names(self):
		# Throw away individual losses and replace output name since this is hidden from the user.
		assert len(self.trainable_model.output_names) == 2
		dummy_output_name = self.trainable_model.output_names[1]
		model_metrics = [name for idx, name in enumerate(self.trainable_model.metrics_names) if idx not in (1, 2)]
		model_metrics = [name.replace(dummy_output_name + '_', '') for name in model_metrics]

		names = model_metrics + self.policy.metrics_names[:]
		# if self.processor is not None:
		# 	names += self.processor.metrics_names[:]
		return names

	def __init__(self, systemState):
		self.systemState = systemState
		self.numActions = len(offloadingDecision.possibleActions)
		self.gamma = sim.constants.GAMMA

		sim.debug.out(sim.constants.OFFLOADING_POLICY)
		self.policy = rl.policy.EpsGreedyQPolicy(eps=sim.constants.EPS)
		# self.dqn = rl.agents.DQNAgent(model=self.model, policy=rl.policy.LinearAnnealedPolicy(, attr='eps', value_max=sim.constants.EPS_MAX, value_min=sim.constants.EPS_MIN, value_test=.05, nb_steps=sim.constants.EPS_STEP_COUNT), enable_double_dqn=False, gamma=.99, batch_size=1, nb_actions=self.numActions)
		self.optimizer = keras.optimizers.Adam(lr=sim.constants.LEARNING_RATE)
		# self.dqn.compile(self.optimizer, metrics=['mae'])
		# self.dqn.training = True

		self.createModel()

		self.history = dict()
		self.history["loss"] = []
		self.history["reward"] = []
		self.history["q"] = []
		self.history["action"] = []

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
		if sim.debug.enabled:
			self.model.summary()


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
		lossOut = keras.layers.Lambda(clipped_masked_error, output_shape=(1,), name='loss')([correctQ, predictedQ, mask])
		# this copies the existing model
		ins = [self.model.input] if type(self.model.input) is not list else self.model.input
		self.trainable_model = keras.models.Model(inputs=ins + [correctQ, mask], outputs=[lossOut, predictedQ])
		assert len(self.trainable_model.output_names) == 2
		combined_metrics = {self.trainable_model.output_names[1]: metrics}
		losses = [
			lambda correctQ, predictedQ: predictedQ,  # loss is computed in Lambda layer
			lambda correctQ, predictedQ: tf.keras.backend.zeros_like(predictedQ),  # we only include this for the metrics
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
	def forward(self):
		self.beforeState = np.array(sim.systemState.current.currentState)
		sim.debug.out("beforestate {}".format(sim.systemState.current.currentState))
		qValues = self.model.predict(self.beforeState.reshape((1, 1, self.systemState.stateCount)))[0]
		sim.debug.out('q {}'.format(qValues))
		actionIndex = self.policy.select_action(q_values=qValues)
		self.latestAction = actionIndex

		choice = offloadingDecision.possibleActions[actionIndex]
		sim.debug.out("choice: {}".format(choice), 'r')
		# must set local choices index
		if choice.local:
			choice.targetDeviceIndex = self.systemState.selfDeviceIndex
		# return agent.decodeIndex(actionIndex, options)
		return choice

	# update based on resulting system state and reward
	def backward(self, reward, finished):
		metrics = [np.nan for _ in self.metrics_names]

		# Compute the q_values given state1, and extract the maximum for each sample in the batch.
		# We perform this prediction on the target_model instead of the model for reasons
		# outlined in Mnih (2015). In short: it makes the algorithm more stable.
		target_q_values = self.model.predict_on_batch(np.array([np.array([np.array(sim.systemState.current.currentState)])])) # TODO: target_model
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
		targets[0, self.latestAction] = R  # update action with estimated accumulated reward
		dummy_targets[0] = R
		masks[0, self.latestAction] = 1.  # enable loss for this specific action

		targets = np.array(targets).astype('float32')
		masks = np.array(masks).astype('float32')


		# Finally, perform a single update on the entire batch. We use a dummy target since
		# the actual loss is computed in a Lambda layer that needs more complex input. However,
		# it is still useful to know the actual target to compute metrics properly.
		x = [np.array([[self.beforeState]])] + [targets, masks]
		y = [dummy_targets, targets]

		self.trainable_model._make_train_function()
		metrics = self.trainable_model.train_on_batch(x, y)
		# metrics = metrics[1:3]
		metrics = [metric for idx, metric in enumerate(metrics) if idx not in (1, 2)]  # throw away individual losses
		metrics += self.policy.metrics
		# print(metrics, self.metrics_names)

		# new metrics
		self.loss = metrics[0]
		self.latestReward = R
		self.latestMAE = metrics[1]
		self.latestMeanQ = metrics[2]

		# metrics history
		self.history["loss"].append(self.loss)
		self.history["reward"].append(self.latestReward)
		self.history["q"].append(self.latestMeanQ)

		# print('reward', reward)

		sim.debug.out("loss: {} reward: {}".format(self.loss, self.latestReward), 'r')
		print("loss: {} reward: {}".format(self.loss, self.latestReward), 'r')

		# agent.step += 1
		# agent.update_target_model_hard()

		# return metrics