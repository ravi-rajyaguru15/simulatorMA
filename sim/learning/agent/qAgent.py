import traceback

import numpy as np

from sim import debug, counters
from sim.learning.agent.agent import agent
from sim.offloading.offloadingPolicy import REINFORCEMENT_LEARNING
from sim.simulations import constants


class qAgent(agent):
	__name__ = "Q Agent"
	targetModel = None
	precache = None
	
	# def reward(self, job, task, device):
	# 	# default reward behaviour
	# 	jobReward = 1 if job.finished else 0
	# 	deadlineReward = 0 if job.deadlineMet() else -0.5
	# 	expectedLifetimeReward = -.5 if (job.startExpectedLifetime - job.systemLifetime()) > (
	# 				job.currentTime - job.createdTime) else 0  # reward if not reducing lifetime more than actual duration
	# 	simulationDoneReward = -100 if job.episodeFinished() else 0
	#
	# 	debug.learnOut(
	# 		'reward: job {} deadline {} expectedLife {} simulationDone {}'.format(jobReward, deadlineReward,
	# 																			  expectedLifetimeReward,
	# 																			  simulationDoneReward), 'b')
	# 	# traceback.print_stack()
	#
	# 	return jobReward + deadlineReward + expectedLifetimeReward + simulationDoneReward

	# update based on resulting system state and reward
	def backward(self, job, task, device, episodeFinished):
		reward = self.reward(job=job, task=task, device=device)
		# reward = self.reward(job, task, device)
		finished = episodeFinished

		debug.out(debug.formatDebug("backward {} {}", (reward, finished)), 'y')
		debug.out("\n")
		# traceback.print_stack()
		# debug.learnOut("\n")

		self.totalReward += reward
		self.episodeReward += reward

		counters.NUM_BACKWARD += 1

		# update model here
		# if job.beforeState 4 and job.beforeState[1] == 0:
		# 	print("training", job, "from", cause)

		if None in job.beforeState:
			print("cannot train, none beforestate")
		else:
			self.addTrainingData(job.latestAction, reward, job.beforeState, self.systemState, finished)

			# self.trainModel(job.latestAction, reward, job.beforeState, self.systemState, finished)

		# new metrics
		self.latestReward = reward
		self.latestAction = job.latestAction
		# self.latestR = R

		# debug.learnOut\
		# diff = self.systemState - job.beforeState
		np.set_printoptions(precision=3)
		# debug.infoOut("{}, created: {:6.3f} {:<7}: {}, deadline: {:9.5f} ({:10.5f}), action: {:<9}, expectedLife (before: {:9.5f} - after: {:9.5f}) = {:10.5f}, reward: {}".format(job.currentTime, job.createdTime, str(job), int(job.finished), job.deadlineRemaining(), (job.currentTime - job.createdTime), str(self.possibleActions[job.latestAction]), job.beforeState.	getField("selfExpectedLife")[0], self.systemState.getField("selfExpectedLife")[0], diff["selfExpectedLife"][0], reward))
		# print("state diff: {}".format(diff).replace("array", ""), 'p')

		# save to history
		job.addToHistory(self.latestReward, self.latestMeanQ, self.latestLoss)

		# # metrics history
		# self.history.add("loss", self.loss)
		# self.history["reward"].append(self.latestReward)
		# self.history["q"].append(self.latestMeanQ)

		# print('reward', reward)

		debug.infoOut(debug.formatInfo("loss: {} reward: {}", (self.latestLoss, self.latestReward)), 'r')
		# debug.learnOut("loss: {} reward: {} R: {}".format(self.latestLoss, self.latestReward, self.latestR), 'r')
	#
	# agent.step += 1
	# agent.update_target_model_hard()

	# return metrics

	# prepares and either caches or affects training data
	def addTrainingData(self, latestAction, reward, beforeState, afterState, finished):
		assert not self.productionMode

		# prepare training data
		# beforeState = np.array(beforeState).reshape(beforeState.shape[0])
		beforeState = np.array(beforeState)
		beforeStateIndex = afterState.getIndex(beforeState)

		afterStateIndex = afterState.getIndex()

		trainingDatapoint = (latestAction, reward, beforeState, beforeStateIndex, afterStateIndex, finished)

		# either add to training list or immediately train
		if self.offPolicy:
			self.trainingData.append(trainingDatapoint)
			# self.trainingTargets.append(targetQ)
		else:
			self.trainBatch([trainingDatapoint])
			# model.train_on_batch(beforeStates, targetQ)

	def updateModel(self):
		assert self.offPolicy
		assert not self.productionMode

		self.trainBatch(self.trainingData)

		if self.precache:
			self.cachePredictions()
		else:
			self.predictions = dict()

		self.trainingData, self.trainingTargets = [], []

		# self.targetModel.set_weights(self.model.get_weights())

	def prepareTrainingDatapoint(self, datapoint):
		latestAction, reward, beforeState, beforeStateIndex, afterStateIndex, finished = datapoint
		
		# old Q value
		# directly based on trainModel from qTableAgent
		# Q before
		beforeQ = self.predict(beforeStateIndex) # self.predictions[beforeStateIndex]
		
		Qsa = beforeQ[latestAction]
		
		# Q after
		maxQ = np.argmax(self.predict(afterStateIndex))

		# calculate new Q
		target = reward + constants.GAMMA * maxQ
		increment = constants.LEARNING_RATE * (target - Qsa)
		
		# same update as qtable
		targetQ = np.array(beforeQ)
		targetQ[latestAction] = Qsa + increment

		self.latestLoss = (target - Qsa) ** 2.
		self.latestMeanQ = np.mean(beforeQ)

		return beforeState, beforeStateIndex, targetQ

	def recachePredictions(self):
		pass

	def cachePredictions(self):
		# perform predictions for all possible states 
		# collect input states
		inputStates = []
		for i in range(self.systemState.getUniqueStates()):
			inputStates.append(self.systemState.fromIndex(i).currentState)
		inputStates = np.array(inputStates)
		
		# perform all predictions
		listPredictions = self.predictBatch(inputStates)

		# assemble dict
		self.predictions = dict()
		for i in range(self.systemState.getUniqueStates()):
			self.predictions[i] = listPredictions[i]

	def chooseDestination(self, task, job, device):
		debug.out("deciding how to offload new job", 'y')
		debug.out("owner: {}".format(self.owner), 'r')
		# print("choose", task, job, device)
		choice = self.firstDecideDestination(task, job, device)
		return choice

	def getPolicyMetrics(self):
		return []

	def train(self, task, job, device, cause=None):
		if not self.productionMode:
			# debug.learnOut("Training: [{}] [{}] [{}]".format(task, job, device), 'y')
			debug.learnOut(debug.formatLearn("Training %s for %s %d %s %s", (device, job, job.latestAction, cause, job.beforeState)), 'y')
			if device.gracefulFailure: debug.learnOut("graceful failure %s" % job.beforeState, 'y')
			self.systemState.updateState(task, job, device)

			if cause is None:
				traceback.print_stack()

			self.backward(job, episodeFinished=job.episodeFinished(), task=task, device=device)
			debug.infoOut(debug.formatInfo("train: %s %s %s A %s R %.2f", (task, job, device, self.getAction(job.latestAction), self.latestReward)))
			debug.infoOut(debug.formatInfo("to     %s %d", (self.systemState.getStateDescription(enabled=debug.settings.infoEnabled, index=self.systemState.getIndex()))))
			debug.infoOut(debug.formatInfo("from   %s", self.systemState.getStateDescription(index=self.systemState.getIndex(job.beforeState), enabled=debug.settings.infoEnabled)))

			job.reset()

	genericException = Exception("Not implemented in generic Q agent")
	def predict(self, state):
		raise self.genericException
	def predictBatch(self, states):
		raise self.genericException


	def createModel(self):
		raise self.genericException

	def trainModel(self, latestAction, R, beforeState, afterState, finished):
		raise self.genericException



	def saveModel(self):
		raise self.genericException


	def loadModel(self):
		raise self.genericException
