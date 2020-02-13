from rl.policy import EpsGreedyQPolicy
from rl.util import huber_loss
from tensorflow import keras
from keras.backend import mean, max
import tensorflow as tf
import numpy as np

from sim import debug
from sim.learning.agent.agent import agent
from sim.simulations import constants
from sim.simulations.variable import Uniform


class qTableAgent(agent):
	metrics_names = None
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

	def __init__(self, systemState):
		self.gamma = constants.GAMMA
		self.policy = Uniform(.5, 1)

		print("Q TABLE AGENT")
		debug.out("Q Table agent: %s" % constants.OFFLOADING_POLICY)
		# self.dqn = rl.agents.DQNAgent(model=self.model, policy=rl.policy.LinearAnnealedPolicy(, attr='eps', value_max=sim.constants.EPS_MAX, value_min=sim.constants.EPS_MIN, value_test=.05, nb_steps=sim.constants.EPS_STEP_COUNT), enable_double_dqn=False, gamma=.99, batch_size=1, nb_actions=self.numActions)

		agent.__init__(self, systemState)

	def createModel(self):
		# create Q table
		self.model = np.zeros((2 ** self.systemState.stateCount, self.numActions)) # assuming binary states TODO: number of states

	def trainModel(self, latestAction, R, beforeState):
		index = beforeState.getIndex()
		self.model[index, latestAction] += R

	def predict(self, state):
		# find row from q table for this state
		return self.model[state.getIndex(), :] # TODO: figure out which row is the correct one

	# def predictBatch(self, stateBatch):
	# 	return self.model.predict_on_batch(stateBatch)

	def selectAction(self, qValues):
		# EPS greedy
		if self.policy.evaluate(constants.EPS):
			# return random
			action = np.random.randint(0, self.numActions - 1)
			print('selecting random in', qValues, action)
			return action
		else:
			print('selecting max from', qValues, np.argmax(qValues))
			return np.argmax(qValues)


def mean_q(correctQ, predictedQ):
	return mean(max(predictedQ, axis=-1))

