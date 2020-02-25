import math
import sys

import numpy as np
# import tensorflow as tf
from keras.backend import mean, max as kerasMax
from rl.policy import EpsGreedyQPolicy
from rl.util import huber_loss
from tensorflow import keras

from sim import debug
from sim.learning.agent.agent import agent
from sim.learning.agent.qAgent import qAgent
from sim.simulations import constants
from sim.simulations.variable import Uniform


class qTableAgent(qAgent):
	__name__ = "Q Table Agent"
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

	def __init__(self, systemState, owner=None):
		self.gamma = constants.GAMMA
		self.policy = Uniform(.5, 1)

		debug.out("Q Table agent")
		# self.dqn = rl.agents.DQNAgent(model=self.model, policy=rl.policy.LinearAnnealedPolicy(, attr='eps', value_max=sim.constants.EPS_MAX, value_min=sim.constants.EPS_MIN, value_test=.05, nb_steps=sim.constants.EPS_STEP_COUNT), enable_double_dqn=False, gamma=.99, batch_size=1, nb_actions=self.numActions)

		agent.__init__(self, systemState, owner=owner)

	def createModel(self):
		# create Q table
		print("qtable:", (self.systemState.getUniqueStates(), self.numActions))
		self.model = np.zeros((self.systemState.getUniqueStates(), self.numActions))

	def trainModel(self, latestAction, reward, beforeState, currentState, finished):
		beforeIndex = beforeState.getIndex()
		Qsa = self.model[beforeIndex, latestAction]
		currentIndex = currentState.getIndex()
		maxQ = np.argmax(self.model[currentIndex, :])
		target = reward + constants.GAMMA * maxQ
		increment = constants.LEARNING_RATE * (target - Qsa)
		debug.learnOut("updating qtable: %d\t%d\t%f\t%f" % (beforeIndex, latestAction, increment, reward))

		# Q learning 101:
		self.model[beforeIndex, latestAction] = Qsa + increment
		self.latestLoss = (target - Qsa) ** 2.
		self.latestMeanQ = np.mean(self.model[beforeIndex, :])


	def predict(self, state):
		# find row from q table for this state
		return self.model[state.getIndex(), :] # TODO: figure out which row is the correct one

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
				entry += "{:10.4f}".format(self.model[i, j]) + " "
			entry += " ]"
			print(description, entry)

			maxEntryWorth = max(len(description), maxEntryWorth)

		formattedString = ""
		for formattedAction in ["%11s" % action for action in self.possibleActions]:
			formattedString += formattedAction
		print("%s%s" % (" " * (maxEntryWorth+1), formattedString))


def mean_q(correctQ, predictedQ):
	return mean(kerasMax(predictedQ, axis=-1))

