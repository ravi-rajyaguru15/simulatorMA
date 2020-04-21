import math
import os
import pickle
import sys
from copy import deepcopy
from random import random, choice

import numpy as np
# import tensorflow as tf
# from keras.backend import mean, max as kerasMax
# from rl.policy import EpsGreedyQPolicy
# from rl.util import huber_loss
# from tensorflow import keras
from numpy.core.multiarray import ndarray

from sim import debug
from sim.learning.agent.agent import agent
from sim.learning.agent.qAgent import qAgent
from sim.learning.state.discretisedSystemState import discretisedSystemState
from sim.learning.state.systemState import systemState
from sim.simulations import constants, localConstants
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

	def __init__(self, systemState, reconsiderBatches, allowExpansion=constants.ALLOW_EXPANSION, owner=None, offPolicy=constants.OFF_POLICY):
		self.gamma = constants.GAMMA
		self.policy = Uniform(.5, 1)
		self.allowExpansion = allowExpansion

		debug.out("Q Table agent")
		# self.dqn = rl.agents.DQNAgent(model=self.model, policy=rl.policy.LinearAnnealedPolicy(, attr='eps', value_max=sim.constants.EPS_MAX, value_min=sim.constants.EPS_MIN, value_test=.05, nb_steps=sim.constants.EPS_STEP_COUNT), enable_double_dqn=False, gamma=.99, batch_size=1, nb_actions=self.numActions)

		qAgent.__init__(self, systemState, reconsiderBatches=reconsiderBatches, owner=owner, offPolicy=offPolicy)

	def createModel(self):
		# create Q table
		debug.learnOut("qtable: (%d, %d)" % (self.systemState.getUniqueStates(), self.numActions))
		self.model = qTable(self.systemState.getUniqueStates(), self.numActions, "Model")
		if self.offPolicy:
			self.targetModel = qTable(self.systemState.getUniqueStates(), self.numActions, "Target Model")

	def expandModel(self):
		pass

	def trainModel(self, latestAction, reward, beforeState, currentState, finished):
		beforeIndex = self.systemState.getIndex(beforeState)
		Qsa = self.model.getQ(beforeIndex, latestAction)
		beforeQ = np.array(self.model.getQ(beforeIndex))
		currentIndex = currentState.getIndex()
		maxQ = np.argmax(self.model.getQ(currentIndex))
		target = reward + constants.GAMMA * maxQ
		increment = constants.LEARNING_RATE * (target - Qsa)
		# debug.learnOut("updating qtable: %d\t%d\t%f\t%f" % (beforeIndex, latestAction, increment, reward))

		# Q learning 101:
		trainModel = self.targetModel if self.offPolicy else self.model
		trainModel.setQ(beforeIndex, action=latestAction, value=Qsa + increment)
		self.latestLoss = (target - Qsa) ** 2.
		self.latestMeanQ = self.model.meanQ(beforeState)

		# if beforeState[0] == 4 and beforeState[1] == 0:
		debug.learnOut(debug.formatLearn("training %d before: %s current: %s r: %.2f %s %s", (latestAction, beforeState, currentState, reward, beforeQ, trainModel.getQ(beforeIndex))))

	def predict(self, state):
		# find row from q table for this state
		return self.model.getQ(state) # TODO: figure out which row is the correct one

	# def predictBatch(self, stateBatch):
	# 	return self.model.predict_on_batch(stateBatch)

	def selectAction(self, systemState):
		index = self.systemState.getIndex(systemState)
		# EPS greedy
		if self.policy.evaluate(constants.EPS) and not self.productionMode:
			# return random
			action = np.random.randint(0, self.numActions)
			# if systemState[0] == 4:
			# 	print("random", action, systemState)
			# print('selecting random in', qValues, action)
			return action
		else:
			qValues = self.predict(index)
			best = np.max(qValues)
			indexes = np.where(qValues == best)[0]
			chosen = choice(indexes)
			# if systemState[0] == 4 and systemState[1] == 0:
			# debug.learnOut("chose: {} ({}) {} {}".format(best, self.possibleActions[best], systemState, np.array(qValues)), 'r')

			return chosen

	def printModel(self):
		self._printModel(self.model)

	def printTargetModel(self):
		if self.targetModel is not None:
			self._printModel(self.targetModel)
		else:
			print("No target model available...")

	def _printModel(self, model):
		print()
		print("%s %s" % (self, model))
		maxEntryWorth = 0
		for i in range(model.stateCount):
			description = self.systemState.getStateDescription(i)
			entry = "["
			for j in range(model.actionCount):
				entry += "{:10.4f}".format(model.getQ(i, j)) + " "
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
		# print(originalState.getUniqueStates(), self.systemState.getUniqueStates())
		self.model.expand()
		if self.offPolicy:
			self.targetModel.expand()
		self.importQTable(sourceTable=originalModel, sourceSystemState=originalState)

	def importQTable(self, sourceTable, sourceSystemState):
		mapping = discretisedSystemState.convertIndexMap(sourceSystemState, self.systemState)
		# print("mapping", mapping)
		for i in range(len(mapping)):
			self.model.setQ(mapping[i], sourceTable.getQ(i))
		if self.offPolicy:
			qTable.copyModel(self.model, self.targetModel)

	def updateTargetModel(self):
		assert self.offPolicy
		if not self.productionMode:
			qTable.copyModel(self.targetModel, self.model)

	def saveModel(self):
		pickle.dump(self.model, open(localConstants.OUTPUT_DIRECTORY + "/model.pickle", 'wb'))
		if self.targetModel is not None:
			pickle.dump(self.targetModel, open(localConstants.OUTPUT_DIRECTORY + "/targetModel.pickle", 'wb'))

	def loadModel(self):
		if os.path.exists(localConstants.OUTPUT_DIRECTORY + "/model.pickle"):
			self.model = pickle.load(open(localConstants.OUTPUT_DIRECTORY + "/model.pickle", 'rb'))
			if self.offPolicy:
				self.targetModel = pickle.load(open(localConstants.OUTPUT_DIRECTORY + "/targetModel.pickle", 'rb'))
			return True
		else:
			return False

class qTable:
	table = None
	stateCount = None
	actionCount = None
	name = None

	def __init__(self, stateCount, actionCount, name):
		self.table = np.zeros((stateCount, actionCount)) + constants.INITIAL_Q
		self.stateCount = stateCount
		self.actionCount = actionCount
		self.name = name

	def __repr__(self): return self.name

	# increase size of existing table
	def expand(self):
		self.stateCount *= 2
		self.table = np.zeros((self.stateCount, self.actionCount)) + constants.INITIAL_Q

	def getQ(self, state, action=None):
		if isinstance(state, discretisedSystemState):
			state = state.getIndex()

		# print("getq", state)
		assert state < self.stateCount

		if action is None:
			return self.table[state, :]
		else:
			return self.table[state, action]

	def setQ(self, state, value, action=None):
		if isinstance(state, discretisedSystemState):
			state = state.getIndex()
		assert state < self.stateCount
		if action is None:
			self.table[state, :] = value
		else:
			self.table[state, action] = value

	def meanQ(self, state):
		if isinstance(state, discretisedSystemState):
			state = state.getIndex()
		return np.mean(self.table[state, :])

	@staticmethod
	def copyModel(source, destination):
		assert source.stateCount == destination.stateCount and source.actionCount == destination.actionCount
		destination.table[:, :] = source.table[:, :]


# def mean_q(correctQ, predictedQ):
# 	return mean(kerasMax(predictedQ, axis=-1))

