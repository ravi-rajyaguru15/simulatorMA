import math
import sys
from copy import deepcopy

import numpy as np
# import tensorflow as tf
# from keras.backend import mean, max as kerasMax
# from rl.policy import EpsGreedyQPolicy
# from rl.util import huber_loss
# from tensorflow import keras

from sim import debug
from sim.learning.agent.agent import agent
from sim.learning.agent.qAgent import qAgent
from sim.learning.state.discretisedSystemState import discretisedSystemState
from sim.learning.state.systemState import systemState
from sim.simulations import constants
from sim.simulations.variable import Uniform


class qTableAgent(qAgent):
	# def __repr__(self): return "<Q Table Agent>"
	# @property
	# def metrics_names(self):
	# 	# Throw away individual losses and replace output name since this is hidden from the user.
	# 	assert len(self.trainable_model.output_names) == 2
	# 	dummy_output_name = self.trainable_model.output_names[1]
	# 	model_metrics = [name for idx, name in enumerate(self.trainable_model.metrics_names) if idx not in (1, 2)]
	# 	model_metrics = [name.replace(dummy_output_name + '_', '') for name in model_metrics]
	#
	# 	names = model_metrics + self.policy.metrics_names[:]
	#
	# 	return names

	allowExpansion = None

	def __init__(self, systemState, allowExpansion=constants.ALLOW_EXPANSION, owner=None):
		self.gamma = constants.GAMMA
		self.policy = Uniform(.5, 1)
		self.allowExpansion = allowExpansion

		debug.out("Q Table agent")
		# self.dqn = rl.agents.DQNAgent(model=self.model, policy=rl.policy.LinearAnnealedPolicy(, attr='eps', value_max=sim.constants.EPS_MAX, value_min=sim.constants.EPS_MIN, value_test=.05, nb_steps=sim.constants.EPS_STEP_COUNT), enable_double_dqn=False, gamma=.99, batch_size=1, nb_actions=self.numActions)

		agent.__init__(self, systemState, owner=owner)

	def createModel(self):
		# create Q table
		debug.learnOut("qtable: (%d, %d)" % (self.systemState.getUniqueStates(), self.numActions))
		self.model = qTable(self.systemState.getUniqueStates(), self.numActions)

	def expandModel(self):
		pass

	def trainModel(self, latestAction, reward, beforeState, currentState, finished):
		# beforeIndex = beforeState.getIndex()
		Qsa = self.model.getQ(beforeState, latestAction)
		currentIndex = currentState.getIndex()
		maxQ = np.argmax(self.model.getQ(currentIndex))
		target = reward + constants.GAMMA * maxQ
		increment = constants.LEARNING_RATE * (target - Qsa)
		debug.learnOut("updating qtable: %d\t%d\t%f\t%f" % (beforeState.getIndex(), latestAction, increment, reward))

		# Q learning 101:
		self.model.setQ(beforeState, action=latestAction, value=Qsa + increment)
		self.latestLoss = (target - Qsa) ** 2.
		self.latestMeanQ = self.model.meanQ(beforeState)


	def predict(self, state):
		# find row from q table for this state
		return self.model.getQ(state.getIndex()) # TODO: figure out which row is the correct one

	# def predictBatch(self, stateBatch):
	# 	return self.model.predict_on_batch(stateBatch)

	def selectAction(self, systemState):
		# EPS greedy
		if self.policy.evaluate(constants.EPS):
			# return random
			action = np.random.randint(0, self.numActions - 1)
			# print('selecting random in', qValues, action)
			return action
		else:
			qValues = self.predict(systemState)
			# print('selecting max from', qValues, np.argmax(qValues))
			return np.argmax(qValues)

	def printModel(self):
		print()
		print("%s Model" % self)
		maxEntryWorth = 0
		for i in range(self.systemState.getUniqueStates()):
			description = self.systemState.getStateDescription(i)
			entry = "["
			for j in range(self.numActions):
				entry += "{:10.4f}".format(self.model.getQ(i, j)) + " "
			entry += " ]"
			print(description, entry)

			maxEntryWorth = max(len(description), maxEntryWorth)

		formattedString = ""
		for formattedAction in ["%11s" % action for action in self.possibleActions]:
			formattedString += formattedAction
		print("%s%s" % (" " * (maxEntryWorth+1), formattedString))

	def expandField(self, field):
		originalState = deepcopy(self.systemState)
		originalModel = deepcopy(self.model)
		self.systemState.expandField(field)
		print(originalState.getUniqueStates(), self.systemState.getUniqueStates())
		self.model.expand()
		self.importQTable(sourceTable=originalModel, sourceSystemState=originalState)

	def importQTable(self, sourceTable, sourceSystemState):
		mapping = discretisedSystemState.convertIndexMap(sourceSystemState, self.systemState)
		# print("mapping", mapping)
		for i in range(len(mapping)):
			self.model.setQ(mapping[i], sourceTable.getQ(i))

class qTable:
	table = None

	def __init__(self, stateCount, actionCount):
		self.table = np.zeros((stateCount, actionCount))

	# increase size of existing table
	def expand(self):
		self.table = np.zeros((self.table.shape[0] * 2, self.table.shape[1]))

	def getQ(self, state, action=None):
		if isinstance(state, discretisedSystemState):
			state = state.getIndex()

		if action is None:
			return self.table[state, :]
		else:
			return self.table[state, action]

	def setQ(self, state, value, action=None):
		if isinstance(state, discretisedSystemState):
			state = state.getIndex()
		if action is None:
			self.table[state, :] = value
		else:
			self.table[state, action] = value

	def meanQ(self, state):
		if isinstance(state, discretisedSystemState):
			state = state.getIndex()
		return np.mean(self.table[state, :])


# def mean_q(correctQ, predictedQ):
# 	return mean(kerasMax(predictedQ, axis=-1))

