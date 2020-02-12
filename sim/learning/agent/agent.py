import tensorflow as tf
import numpy as np

import sim
from sim import debug, counters
from sim.learning import offloadingDecision
from sim.learning.action import offloading, LOCAL, BATCH
from sim.learning.systemState import systemState
from sim.simulations import constants


class agent:
	possibleActions = None  # TODO: offloading to self

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

	def __init__(self, systemState):
		self.systemState = systemState

		self.totalReward = 0
		self.reset()

		# self.setDevices(devices)

	def reset(self):
		self.episodeReward = 0

	# self.history = sim.history.history()

	def setDevices(self, devices):
		# self.devices = devices
		# create actions
		# global possibleActions
		# global devices
		assert devices is not None
		self.possibleActions = [offloading(i) for i in range(len(devices))] + [BATCH, LOCAL]
		for i in range(len(self.possibleActions)):
			self.possibleActions[i].index = i
		print('actions', self.possibleActions)
		offloadingDecision.numActionsPerDevice = len(self.possibleActions)

		self.numActions = len(self.possibleActions)

		# needs numActions
		self.createModel()

		self.devices = devices
		# return self.possibleActions

	# # convert decision to a specific action
	# @staticmethod
	# def decodeIndex(index, options):
	# 	# deviceIndex = int(index / numActionsPerDevice)
	# 	# actionIndex = index - deviceIndex * numActionsPerDevice
	# 	# sim.debug.out(index, options)
	# 	# result = decision(options[deviceIndex], action=possibleActions[actionIndex])
	# 	# result = decision(options)
	# 	return result

	def updateState(self, task, job, device):
		# update state
		self.systemState.update(task, job, device)

	# predict best action using Q values
	def forward(self, task, job, device):
		self.updateState(task, job, device)

		debug.learnOut("forward", 'y')
		assert self.model is not None

		counters.NUM_FORWARD += 1

		currentSim = sim.simulations.Simulation.currentSimulation
		job.beforeState = systemState.fromSystemState(currentSim)
		sim.debug.out("beforestate {}".format(job.beforeState))
		qValues = self.predict(job.beforeState.currentState.reshape((1, 1, self.systemState.stateCount)))
		# sim.debug.learnOut('q {}'.format(qValues))
		actionIndex = self.selectAction(qValues)
		job.latestAction = actionIndex
		job.history.add("action", actionIndex)
		# sim.debug.learnOut("chose action {}".format(actionIndex))
		# self.history["action"].append(float(self.latestAction))

		assert self.possibleActions is not None
		choice = self.possibleActions[actionIndex]
		sim.debug.learnOut("choice: {} ({})".format(choice, actionIndex), 'r')

		choice.updateTargetDevice(owner=device, devices=self.devices)
		# choice.updateTargetDevice(devices=self.devices)
		return choice

	genericException = Exception("Not implemented in generic agent")
	def predict(self, state):
		raise self.genericException
	def createModel(self):
		raise self.genericException
	def selectAction(self, qValues):
		raise self.genericException

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
			np.array([np.array([np.array(self.systemState.currentState)])]))  # TODO: target_model
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
		diff = self.systemState - job.beforeState
		np.set_printoptions(precision=3)
		sim.debug.infoOut("{}, created: {:6.3f} {:<7}: {}, deadline: {:9.5f} ({:10.5f}), action: {:<9}, expectedLife (before: {:9.5f} - after: {:9.5f}) = {:10.5f}, reward: {}".format(job.currentTime, job.createdTime, str(job), int(job.finished), job.deadlineRemaining(), (job.currentTime - job.createdTime), str(self.possibleActions[job.latestAction]), job.beforeState.	getField("selfExpectedLife")[0], self.systemState.getField("selfExpectedLife")[0], diff["selfExpectedLife"][0], reward))
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

