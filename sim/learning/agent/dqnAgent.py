import os
import pickle

import numpy as np
import tensorflow as tf
from copy import deepcopy

from keras.backend import mean, max
from rl.policy import EpsGreedyQPolicy
from rl.util import huber_loss
from tensorflow import keras

from sim import debug
from sim.learning.agent.agent import agent
from sim.learning.agent.qAgent import qAgent
from sim.simulations import constants, localConstants
from sim.learning.state.systemState import systemState

class dqnAgent(qAgent):
	__name__ = "Deep Q Agent"

	optimizer = None
	loss = None
	activation = None
	metrics = None
	classification = None
	fullModel = None

	# trainingTargets = None

	predictions = None

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

	def __init__(self, systemState, reconsiderBatches, allowExpansion=constants.ALLOW_EXPANSION, owner=None, offPolicy=constants.OFF_POLICY, loss='binary_crossentropy', activation='relu', metrics=['accuracy'], trainClassification=True, precache=True):
		self.gamma = constants.GAMMA
		self.loss = loss
		self.activation = activation
		self.metrics = metrics
		self.classification = trainClassification
		self.precache = precache

		debug.out("DQN agent created")
		self.policy = EpsGreedyQPolicy(eps=constants.EPS)
		# self.dqn = rl.agents.DQNAgent(model=self.model, policy=rl.policy.LinearAnnealedPolicy(, attr='eps', value_max=sim.constants.EPS_MAX, value_min=sim.constants.EPS_MIN, value_test=.05, nb_steps=sim.constants.EPS_STEP_COUNT), enable_double_dqn=False, gamma=.99, batch_size=1, nb_actions=self.numActions)
		# self.optimizer = keras.optimizers.Adam(lr=constants.LEARNING_RATE)
		self.optimizer = keras.optimizers.RMSprop(lr=constants.LEARNING_RATE)

		# self.trainingTargets = []

		# self.createModel()

		qAgent.__init__(self, systemState, reconsiderBatches=reconsiderBatches, owner=owner, offPolicy=offPolicy)

	def createModel(self, hiddenDepth=1, hiddenWidth=10):
		# import sys
		# sys.exit(0)
		# traceback.print_stack()
		
		# create basic model
		self.fullModel = keras.models.Sequential()
		# self.model.add(keras.layers.Flatten(input_shape=(len(self.systemState.singles),))) 
		self.fullModel.add(keras.Input(shape=(len(self.systemState.singles),)))

		# print("\t", self.systemState, len(self.systemState.singles))
		
		# self.model.add(keras.layers.Flatten(input_shape=(1,) + (len(self.systemState.singles),))) # 3 input
		# print('input shape', (1,) + env.observation_space.shape)

		# hidden layers
		for i in range(hiddenDepth):
			self.fullModel.add(keras.layers.Dense(hiddenWidth, activation=self.activation, kernel_initializer='random_normal', bias_initializer='zeros'))

		# output layers
		if self.classification:
			self.fullModel.add(keras.layers.Dense(self.numActions, activation='relu', name='final', kernel_initializer='random_normal', bias_initializer='zeros'))
		else:
			self.fullModel.add(keras.layers.Dense(self.numActions, activation='linear', name='final', kernel_initializer='random_normal', bias_initializer='zeros'))
		self.fullModel.add(keras.layers.Softmax())

		# create a model that doesn't use the softmax
		self.model = keras.Model(inputs=self.fullModel.input, outputs=self.fullModel.get_layer(name='final').output)

		
		if debug.settings.enabled:
			self.model.summary()
		# self.model.summary()



# intermediate_layer_model = Model(inputs=model.input,
#                                  outputs=model.get_layer(layer_name).output)

		self.model.compile(optimizer=self.optimizer, metrics=self.metrics, loss=self.loss)
		self.fullModel.compile(optimizer=self.optimizer, metrics=self.metrics, loss=self.loss)
		
		# self.createTrainableModel()
		if self.precache:
			self.cachePredictions()
		else:
			self.predictions = dict()
		


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

	def expandField(self, field):

		self.systemState.expandField(field)
	
		self.recachePredictions()


	def recachePredictions(self):
		if self.precache:
			self.cachePredictions()
		else:
			self.predictions = dict()


	def predict(self, state, model=None):
		# if no model provided, assume self.model for Q values
		if model is None: model = self.model

		if self.precache:
			if isinstance(state, int) or isinstance(state, np.int64):
				index = state
			else:
				state = np.array(state, dtype=np.float).reshape((1, state.shape[0]))
				index = int(self.systemState.getIndex(state)[0])

			if index not in self.predictions:
				print("index not found", self.predictions.keys(), index, self.systemState.getUniqueStates())
			assert index in self.predictions
			prediction = self.predictions[index]
		else:
			state = np.array(state, dtype=np.float).reshape((1, state.shape[0]))

			# check if prediction is available
			key = str(state)
			print("key", key, state)
			if key not in self.predictions:
				sys.exit(0)
				self.predictions[key] = self.model.predict(state)[0]
				print("adding prediction", key, self.predictions[key])
			prediction = self.predictions[key]

		return prediction

	def predictBatch(self, states):
		states = tf.convert_to_tensor(states)
		return self.model.predict_on_batch(states)

	def setProductionMode(self, value=True):
		debug.learnOut("switching dqn to production mode!", 'y')
		self.productionMode = value
		self.policy.eps = 0

	def selectAction(self, systemState):
		qValues = self.predict(model=self.model, state=systemState)
		return self.policy.select_action(q_values=qValues)

	# def trainModel(self, latestAction, reward, beforeState, afterState, finished):
	# 	# print(f'training dqn model {latestAction} {reward} {beforeState} {afterState} {finished}')

	# 	self.addTrainingData(latestAction, reward, beforeState, afterState, finished)

	# 	return self.trainModelOnline(latestAction, reward, beforeState, afterState, finished)
	# 	# return self.trainModelBatch(latestAction, reward, [[beforeState]], afterState, finished)

	# def trainModelOnline(self, latestAction, reward, beforeStates, afterState, finished):

	# trainingData is [(latestAction, reward, beforeState, beforeStateIndex, afterStateIndex, finished), ...]
	def prepareTrainingData(self, trainingData):
		trainingX = []
		trainingY = []

		# prepare Q values and actual training data for each
		for datapoint in trainingData:
			beforeState, _, targetQ = self.prepareTrainingDatapoint(datapoint)

			trainingX.append(beforeState)
			trainingY.append(targetQ)
		
		trainingX = np.array(trainingX)
		trainingY = np.array(trainingY)
		
		return trainingX, trainingY
	
	def trainBatch(self, trainingData):
		x, y = self.prepareTrainingData(trainingData)

		# print('training dqn', x.shape, y.shape)
		
		# if not self.productionMode:
		trainedModel = self.fullModel if self.classification else self.model
		
		trainedModel.fit(x, y, verbose=0)

	# def trainModelBatchOnline(self, latestAction, reward, beforeStates, afterState, finished):
	# 	assert self.trainable_model is not None
	# 	assert not self.productionMode

	# 	self.trainable_model = self.fullModel if self.classification else self.model

	# 	# metrics = [np.nan for _ in self.metrics_names]

	# 	# Compute the q_values given state1, and extract the maximum for each sample in the batch.
	# 	# We perform this prediction on the target_model instead of the model for reasons
	# 	# outlined in Mnih (2015). In short: it makes the algorithm more stable.
	# 	# target_q_values =  self.model.predict_on_batch(
	# 	# 	np.array([np.array([np.array(self.systemState.currentState)])]))  # TODO: target_model

	# 	# model = self.model if self.offPolicy else self.targetModel

	# 	# target_q_values = self.predict(self.targetModel, self.systemState.currentState)
	# 	# target_q_values = self.predict(self.targetModel, self.systemState.currentState)
	# 	target_q_values = self.predict(self.model, self.systemState.currentState)


	# 	if self.offPolicy:
	# 		# q_values = self.predict(self.model, self.systemState.currentState)
	# 		actions = np.argmax(target_q_values, axis=0)
	# 		q_batch = np.array([target_q_values[actions]])
	# 	else:
	# 		# print(self.predict(self.systemState), target_q_values)
	# 		q_batch = np.max(target_q_values).flatten()
	# 	# print(q_batch)
	# 	# sys.exit(0)

	# 	# Compute r_t + gamma * max_a Q(s_t+1, a) and update the target targets accordingly,
	# 	# but only for the affected output units (as given by action_batch).
	# 	discounted_reward_batch = self.gamma * q_batch
	# 	# Set discounted reward to zero for all states that were terminal.
	# 	discounted_reward_batch *= [0. if finished else 1.]
	# 	# assert discounted_reward_batch.shape == reward_batch.shape
	# 	R = reward + discounted_reward_batch

	# 	targets = np.zeros((1, self.numActions))
	# 	dummy_targets = np.zeros((1,))
	# 	masks = np.zeros((1, self.numActions))

	# 	targets[0, latestAction] = R  # update action with estimated accumulated reward
	# 	dummy_targets[0] = R
	# 	masks[0, latestAction] = 1.  # enable loss for this specific action

	# 	targets = np.array(targets).astype('float32')
	# 	masks = np.array(masks).astype('float32')

	# 	# Finally, perform a single update on the entire batch. We use a dummy target since
	# 	# the actual loss is computed in a Lambda layer that needs more complex input. However,
	# 	# it is still useful to know the actual target to compute metrics properly.
	# 	x = [np.array(beforeStates)] + [targets, masks]
	# 	y = [dummy_targets, targets]

	# 	print(x)
	# 	print("state:", beforeStates)
	# 	print(y)

	# 	# self.trainable_model._make_train_function()
	# 	metrics = self.trainable_model.train_on_batch(x, y)
	# 	# metrics = metrics[1:3]
	# 	metrics = [metric for idx, metric in enumerate(metrics) if idx not in (1, 2)]  # throw away individual losses
	# 	metrics += self.getPolicyMetrics()
	# 	# print(metrics, self.metrics_names)

	# 	self.latestLoss = metrics[0]
	# 	self.latestMAE = metrics[1]
	# 	self.latestMeanQ = metrics[2]

	# def trainModelBatch(self, beforeStates, actions):
	# 	assert self.trainable_model is not None
	# 	assert not self.productionMode

	# 	# metrics = [np.nan for _ in self.metrics_names]

	# 	# Compute the q_values given state1, and extract the maximum for each sample in the batch.
	# 	# We perform this prediction on the target_model instead of the model for reasons
	# 	# outlined in Mnih (2015). In short: it makes the algorithm more stable.
	# 	# target_q_values =  self.model.predict_on_batch(
	# 	# 	np.array([np.array([np.array(self.systemState.currentState)])]))  # TODO: target_model

	# 	# model = self.model if self.offPolicy else self.targetModel

	# 	# target_q_values = self.predict(self.targetModel, self.systemState.currentState)
	# 	# if self.offPolicy:
	# 	# 	q_values = self.predict(self.model, self.systemState.currentState)
	# 	# 	actions = np.argmax(q_values, axis=0)
	# 	# 	q_batch = np.array([target_q_values[actions]])
	# 	# else:
	# 	# 	# print(self.predict(self.systemState), target_q_values)
	# 	# 	q_batch = np.max(target_q_values).flatten()
	# 	# print(q_batch)
	# 	# sys.exit(0)

	# 	# Compute r_t + gamma * max_a Q(s_t+1, a) and update the target targets accordingly,
	# 	# but only for the affected output units (as given by action_batch).
	# 	# discounted_reward_batch = self.gamma * q_batch
	# 	# # Set discounted reward to zero for all states that were terminal.
	# 	# discounted_reward_batch *= [0. if finished else 1.]
	# 	# # assert discounted_reward_batch.shape == reward_batch.shape
	# 	# R = reward + discounted_reward_batch

	# 	# targets = np.zeros((1, self.numActions))
	# 	# dummy_targets = np.zeros((1,))
	# 	# masks = np.zeros((1, self.numActions))

	# 	# targets[0, latestAction] = R  # update action with estimated accumulated reward
	# 	# dummy_targets[0] = R
	# 	# masks[0, latestAction] = 1.  # enable loss for this specific action

	# 	# targets = np.array(targets).astype('float32')
	# 	# masks = np.array(masks).astype('float32')

	# 	# # Finally, perform a single update on the entire batch. We use a dummy target since
	# 	# # the actual loss is computed in a Lambda layer that needs more complex input. However,
	# 	# # it is still useful to know the actual target to compute metrics properly.
	# 	# x = [np.array(beforeStates)] + [targets, masks]
	# 	# y = [dummy_targets, targets]

	# 	# print(x, "state:", beforeState, y)

	# 	# self.trainable_model._make_train_function()
	# 	print("test")
	# 	metrics = self.model.train_on_batch(beforeStates, actions, return_dict=True)
		
	# 	# metrics = metrics[1:3]
	# 	# metrics = [metric for idx, metric in enumerate(metrics) if idx not in (1, 2)]  # throw away individual losses
	# 	# metrics += self.getPolicyMetrics()
	# 	# print(metrics, self.metrics_names)
	# 	print(metrics)
	# 	self.latestLoss = metrics['loss']
	# 	self.latestMAE = metrics['accuracy']
	# 	self.latestMeanQ = 0# metrics[2]

	def fit(self, beforeStates, actions, epochs, split=0., class_weights=None, batch_size=5):
		verbosity = 2 if debug.settings.enabled else 0

		trainedModel = self.fullModel if self.classification else self.model

		# print("\nfit", beforeStates.shape, actions.shape, '\n')
		# print("FIT TRAIN")

		trainedModel.fit(x=beforeStates, y=actions, batch_size=batch_size, epochs=epochs, validation_split=split, use_multiprocessing=True, verbose=verbosity, class_weight=class_weights)

		# assert not self.offPolicy
		# model learns immediately, not here
		# return


	def saveModel(self, id=""):
		filename = localConstants.OUTPUT_DIRECTORY + f"/models/dqnfullmodel{id}.pickle"
		keras.models.save_model(self.fullModel, filename)
		print(f"saved dqn model {filename}")
		# keras.models.save_model(self.model, localConstants.OUTPUT_DIRECTORY + f"/dqnmodel{id}.pickle")

		# if self.targetModel is not None:
		# 	keras.models.save_model(self.targetModel, localConstants.OUTPUT_DIRECTORY + "/dqntargetModel.pickle")

	def loadModel(self, id=""):
		# print("\n\n\nWARNING: LOADING DQN MODEL\n\n\n")
		filename = localConstants.OUTPUT_DIRECTORY + f"/models/dqnfullmodel{id}.pickle"
		if os.path.exists(filename):
			# self.model = keras.models.load_model(localConstants.OUTPUT_DIRECTORY + f"/dqnmodel{id}.pickle")
			self.fullModel = keras.models.load_model(filename)
			self.model = keras.Model(inputs=self.fullModel.inputs, outputs=self.fullModel.get_layer('final').output)
			# not loading additional model anymore
			# if self.offPolicy:
			# 	self.targetModel = keras.models.load_model(localConstants.OUTPUT_DIRECTORY + "/dqntargetModel.pickle")

			# new model, so predictions change
			if self.precache:
				self.cachePredictions()
			else:
				self.predictions = dict()

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