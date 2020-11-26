import os
import pickle

import numpy as np
import tensorflow as tf

from keras.backend import mean, max
from rl.policy import EpsGreedyQPolicy
from rl.util import huber_loss
from tensorflow import keras

from sim import debug
from sim.learning.agent.agent import agent
from sim.learning.agent.qAgent import qAgent
from sim.simulations import constants, localConstants


class dqnAgent(qAgent):
	__name__ = "Deep Q Agent"

	optimizer = None
	loss = None
	activation = None
	metrics = None
	classification = None
	fullModel = None

	def getPolicyMetrics(self):
		return self.policy.metrics

	@property
	def metrics_names(self):
		# Throw away individual losses and replace output name since this is hidden from the user.
		assert len(self.trainable_model.output_names) == 2
		dummy_output_name = self.trainable_model.output_names[1]
		model_metrics = [name for idx, name in enumerate(self.trainable_model.metrics_names) if idx not in (1, 2)]
		model_metrics = [name.replace(dummy_output_name + '_', '') for name in model_metrics]

		names = model_metrics + self.policy.metrics_names[:]

		return names

	def __init__(self, systemState, reconsiderBatches, allowExpansion=constants.ALLOW_EXPANSION, owner=None, offPolicy=constants.OFF_POLICY, loss='binary_crossentropy', activation='relu', metrics=['accuracy'], trainClassification=True):
		self.gamma = constants.GAMMA
		self.loss = loss
		self.activation = activation
		self.metrics = metrics
		self.classification = trainClassification

		debug.out("DQN agent created")
		self.policy = EpsGreedyQPolicy(eps=constants.EPS)
		# self.dqn = rl.agents.DQNAgent(model=self.model, policy=rl.policy.LinearAnnealedPolicy(, attr='eps', value_max=sim.constants.EPS_MAX, value_min=sim.constants.EPS_MIN, value_test=.05, nb_steps=sim.constants.EPS_STEP_COUNT), enable_double_dqn=False, gamma=.99, batch_size=1, nb_actions=self.numActions)
		# self.optimizer = keras.optimizers.Adam(lr=constants.LEARNING_RATE)
		self.optimizer = keras.optimizers.RMSprop(lr=constants.LEARNING_RATE)


		qAgent.__init__(self, systemState, reconsiderBatches=reconsiderBatches, owner=owner, offPolicy=offPolicy)

	def createModel(self, hiddenDepth=2, hiddenWidth=4):
		# create basic model
		self.fullModel = keras.models.Sequential()
		# self.model.add(keras.layers.Flatten(input_shape=(len(self.systemState.singles),))) 
		self.fullModel.add(keras.Input(shape=(len(self.systemState.singles),)))
		
		# self.model.add(keras.layers.Flatten(input_shape=(1,) + (len(self.systemState.singles),))) # 3 input
		# print('input shape', (1,) + env.observation_space.shape)

		# hidden layers
		for i in range(hiddenDepth):
			self.fullModel.add(keras.layers.Dense(hiddenWidth, activation=self.activation))
			self.fullModel.add(keras.layers.Dense(hiddenWidth, activation=self.activation))

		# # hidden layers
		# self.model.add(keras.layers.Dense(4, activation='relu'))

		# output layers
		if self.classification:
			self.fullModel.add(keras.layers.Dense(self.numActions, activation='relu', name='final'))

			# self.fullModel.add(keras.layers.Dense(self.numActions, activation='softmax', name='final'))
			# self.model = self.fullModel
		else:
			self.fullModel.add(keras.layers.Dense(self.numActions, activation='linear', name='final'))
		self.fullModel.add(keras.layers.Softmax())

			# create a model that doesn't use the softmax
		self.model = keras.Model(inputs=self.fullModel.input, outputs=self.fullModel.get_layer(name='final').output)

		
		if debug.settings.enabled:
			self.model.summary()

# intermediate_layer_model = Model(inputs=model.input,
#                                  outputs=model.get_layer(layer_name).output)

		self.model.compile(optimizer=self.optimizer, metrics=self.metrics, loss=self.loss)
		self.fullModel.compile(optimizer=self.optimizer, metrics=self.metrics, loss=self.loss)
		
		# self.createTrainableModel()

	def createTrainableModel(self):
		raise Exception("not implemented ")
		# # COPIED FROM KERAS-RL LIBRARY
		# # metrics = ['mae']
		# # metrics += [mean_q]  # register default metrics

		# # if self.offPolicy:
		# # 	self.targetModel = clone_model(self.model, custom_objects={})
		# # 	self.targetModel.compile(optimizer=self.optimizer, loss='mse')
		# self.model.compile(optimizer=self.optimizer, loss=self.loss, metrics=self.metrics)

		# def clipped_masked_error(args):
		# 	correctQ, predictedQ, mask = args
		# 	loss = huber_loss(correctQ, predictedQ, np.inf)
		# 	loss *= mask  # apply element-wise mask
		# 	return tf.keras.backend.sum(loss, axis=-1)

		# # Create trainable model. The problem is that we need to mask the output since we only
		# # ever want to update the Q values for a certain action. The way we achieve this is by
		# # using a custom Lambda layer that computes the loss. This gives us the necessary flexibility
		# # to mask out certain parameters by passing in multiple inputs to the Lambda layer.
		# predictedQ = self.model.output
		# correctQ = keras.layers.Input(name='correctQ', shape=(self.numActions,))
		# mask = keras.layers.Input(name='mask', shape=(self.numActions,))
		# lossOut = keras.layers.Lambda(clipped_masked_error, output_shape=(1,), name='loss')(
		# 	[correctQ, predictedQ, mask])
		# # this copies the existing model
		# ins = [self.model.input] if type(self.model.input) is not list else self.model.input
		# self.trainable_model = keras.models.Model(inputs=ins + [correctQ, mask], outputs=[lossOut, predictedQ])
		# assert len(self.trainable_model.output_names) == 2
		# combined_metrics = {self.trainable_model.output_names[1]: metrics}
		# losses = [
		# 	lambda correctQ, predictedQ: predictedQ,  # loss is computed in Lambda layer
		# 	lambda correctQ, predictedQ: tf.keras.backend.zeros_like(predictedQ),
		# 	# we only include this for the metrics
		# ]
		# self.trainable_model.compile(optimizer=self.optimizer, loss=losses, metrics=combined_metrics)

	def predict(self, model, state):
		# print("state", state, state.shape)
		# return model.predict(state.reshape((1, 1, state.shape[0])))[0]
		# state = np.array(state, dtype=np.float).reshape((1,1,state.shape[0]))
		state = np.array(state, dtype=np.float).reshape((1, 2))
		prediction = model.predict(state).flatten()
		
		# print()
		# print("state:", state)
		# print("predict: ", prediction)
		# print()

		return prediction
		# return self.model.predict(state.currentState.reshape((1, 1, state.stateCount)))[0]

	# def predictBatch(self, stateBatch):
	# 	return self.model.predict_on_batch(stateBatch)

	def setProductionMode(self, value=True):
		debug.learnOut("switching dqn to production mode!", 'y')
		self.productionMode = value
		self.policy.eps = 0

	def selectAction(self, systemState):
		qValues = self.predict(self.model, systemState)
		return self.policy.select_action(q_values=qValues)

	def trainModel(self, latestAction, reward, beforeState, afterState, finished):
		return self.trainModelBatch(latestAction, reward, [[beforeState]], afterState, finished)

	def trainModelBatchOnline(self, latestAction, reward, beforeStates, afterState, finished):
		assert self.trainable_model is not None

		metrics = [np.nan for _ in self.metrics_names]

		# Compute the q_values given state1, and extract the maximum for each sample in the batch.
		# We perform this prediction on the target_model instead of the model for reasons
		# outlined in Mnih (2015). In short: it makes the algorithm more stable.
		# target_q_values =  self.model.predict_on_batch(
		# 	np.array([np.array([np.array(self.systemState.currentState)])]))  # TODO: target_model

		# model = self.model if self.offPolicy else self.targetModel

		target_q_values = self.predict(self.targetModel, self.systemState.currentState)
		if self.offPolicy:
			q_values = self.predict(self.model, self.systemState.currentState)
			actions = np.argmax(q_values, axis=0)
			q_batch = np.array([target_q_values[actions]])
		else:
			# print(self.predict(self.systemState), target_q_values)
			q_batch = np.max(target_q_values).flatten()
		# print(q_batch)
		# sys.exit(0)

		# Compute r_t + gamma * max_a Q(s_t+1, a) and update the target targets accordingly,
		# but only for the affected output units (as given by action_batch).
		discounted_reward_batch = self.gamma * q_batch
		# Set discounted reward to zero for all states that were terminal.
		discounted_reward_batch *= [0. if finished else 1.]
		# assert discounted_reward_batch.shape == reward_batch.shape
		R = reward + discounted_reward_batch

		targets = np.zeros((1, self.numActions))
		dummy_targets = np.zeros((1,))
		masks = np.zeros((1, self.numActions))

		targets[0, latestAction] = R  # update action with estimated accumulated reward
		dummy_targets[0] = R
		masks[0, latestAction] = 1.  # enable loss for this specific action

		targets = np.array(targets).astype('float32')
		masks = np.array(masks).astype('float32')

		# Finally, perform a single update on the entire batch. We use a dummy target since
		# the actual loss is computed in a Lambda layer that needs more complex input. However,
		# it is still useful to know the actual target to compute metrics properly.
		x = [np.array(beforeStates)] + [targets, masks]
		y = [dummy_targets, targets]

		# print(x, "state:", beforeState, y)

		self.trainable_model._make_train_function()
		metrics = self.trainable_model.train_on_batch(x, y)
		# metrics = metrics[1:3]
		metrics = [metric for idx, metric in enumerate(metrics) if idx not in (1, 2)]  # throw away individual losses
		metrics += self.getPolicyMetrics()
		# print(metrics, self.metrics_names)

		self.latestLoss = metrics[0]
		self.latestMAE = metrics[1]
		self.latestMeanQ = metrics[2]

	def trainModelBatch(self, beforeStates, actions):
		assert self.trainable_model is not None

		# metrics = [np.nan for _ in self.metrics_names]

		# Compute the q_values given state1, and extract the maximum for each sample in the batch.
		# We perform this prediction on the target_model instead of the model for reasons
		# outlined in Mnih (2015). In short: it makes the algorithm more stable.
		# target_q_values =  self.model.predict_on_batch(
		# 	np.array([np.array([np.array(self.systemState.currentState)])]))  # TODO: target_model

		# model = self.model if self.offPolicy else self.targetModel

		# target_q_values = self.predict(self.targetModel, self.systemState.currentState)
		# if self.offPolicy:
		# 	q_values = self.predict(self.model, self.systemState.currentState)
		# 	actions = np.argmax(q_values, axis=0)
		# 	q_batch = np.array([target_q_values[actions]])
		# else:
		# 	# print(self.predict(self.systemState), target_q_values)
		# 	q_batch = np.max(target_q_values).flatten()
		# print(q_batch)
		# sys.exit(0)

		# Compute r_t + gamma * max_a Q(s_t+1, a) and update the target targets accordingly,
		# but only for the affected output units (as given by action_batch).
		# discounted_reward_batch = self.gamma * q_batch
		# # Set discounted reward to zero for all states that were terminal.
		# discounted_reward_batch *= [0. if finished else 1.]
		# # assert discounted_reward_batch.shape == reward_batch.shape
		# R = reward + discounted_reward_batch

		# targets = np.zeros((1, self.numActions))
		# dummy_targets = np.zeros((1,))
		# masks = np.zeros((1, self.numActions))

		# targets[0, latestAction] = R  # update action with estimated accumulated reward
		# dummy_targets[0] = R
		# masks[0, latestAction] = 1.  # enable loss for this specific action

		# targets = np.array(targets).astype('float32')
		# masks = np.array(masks).astype('float32')

		# # Finally, perform a single update on the entire batch. We use a dummy target since
		# # the actual loss is computed in a Lambda layer that needs more complex input. However,
		# # it is still useful to know the actual target to compute metrics properly.
		# x = [np.array(beforeStates)] + [targets, masks]
		# y = [dummy_targets, targets]

		# print(x, "state:", beforeState, y)

		# self.trainable_model._make_train_function()
		print("test")
		metrics = self.model.train_on_batch(beforeStates, actions, return_dict=True)
		
		# metrics = metrics[1:3]
		# metrics = [metric for idx, metric in enumerate(metrics) if idx not in (1, 2)]  # throw away individual losses
		# metrics += self.getPolicyMetrics()
		# print(metrics, self.metrics_names)
		print(metrics)
		self.latestLoss = metrics['loss']
		self.latestMAE = metrics['accuracy']
		self.latestMeanQ = 0# metrics[2]

	def fit(self, beforeStates, actions, epochs, split=0., class_weights=None, batch_size=5):
		verbosity = 2 if debug.settings.enabled else 0

		trainedModel = self.fullModel if self.classification else self.model

		trainedModel.fit(x=beforeStates, y=actions, batch_size=batch_size, epochs=epochs, validation_split=split, use_multiprocessing=True, verbose=verbosity, class_weight=class_weights)

	def updateTargetModel(self):
		self.targetModel.set_weights(self.model.get_weights())

	def saveModel(self, id=""):
		keras.models.save_model(self.fullModel, localConstants.OUTPUT_DIRECTORY + f"/dqnfullmodel{id}.pickle")
		# keras.models.save_model(self.model, localConstants.OUTPUT_DIRECTORY + f"/dqnmodel{id}.pickle")

		if self.targetModel is not None:
			keras.models.save_model(self.targetModel, localConstants.OUTPUT_DIRECTORY + "/dqntargetModel.pickle")

	def loadModel(self, id=""):
		if os.path.exists(localConstants.OUTPUT_DIRECTORY + f"/dqnfullmodel{id}.pickle"):
			# self.model = keras.models.load_model(localConstants.OUTPUT_DIRECTORY + f"/dqnmodel{id}.pickle")
			self.fullModel = keras.models.load_model(localConstants.OUTPUT_DIRECTORY + "/dqnfullmodel.pickle")
			self.model = keras.Model(inputs=self.fullModel.inputs, outputs=self.fullModel.get_layer('final').output)
			if self.offPolicy:
				self.targetModel = keras.models.load_model(localConstants.OUTPUT_DIRECTORY + "/dqntargetModel.pickle")
			return True
		else:
			print("ERROR: Could not load model", id)
			import sys
			sys.exit(0)
			return False

def mean_q(correctQ, predictedQ):
	return mean(max(predictedQ, axis=-1))

def clone_model(model, custom_objects={}):
	# Requires Keras 1.0.7 since get_config has breaking changes.
	config = {
		'class_name': model.__class__.__name__,
		'config': model.get_config(),
	}
	clone = keras.models.model_from_config(config, custom_objects=custom_objects)
	clone.set_weights(model.get_weights())
	return clone