import traceback

import numpy as np

from sim import debug, counters
from sim.learning.agent.agent import agent
from sim.offloading.offloadingPolicy import REINFORCEMENT_LEARNING
from sim.simulations import constants


class qAgent(agent):
	__name__ = "Q Agent"
	targetModel = None

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

		debug.learnOut("backward {} {}".format(reward, finished), 'y')
		debug.learnOut("\n")
		# traceback.print_stack()
		# debug.learnOut("\n")

		self.totalReward += reward
		self.episodeReward += reward

		counters.NUM_BACKWARD += 1

		# update model here
		# if job.beforeState[0] == 4 and job.beforeState[1] == 0:
		# 	print("training", job, "from", cause)

		self.trainModel(job.latestAction, reward, job.beforeState, self.systemState, finished)

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

		debug.learnOut("loss: {} reward: {}".format(self.latestLoss, self.latestReward), 'r')
		# debug.learnOut("loss: {} reward: {} R: {}".format(self.latestLoss, self.latestReward, self.latestR), 'r')
	#
	# agent.step += 1
	# agent.update_target_model_hard()

	# return metrics

	def chooseDestination(self, task, job, device):
		debug.learnOut("deciding how to offload new job", 'y')
		debug.learnOut("owner: {}".format(self.owner), 'r')
		choice = self.firstDecideDestination(task, job, device)
		# print("destination chosen", choice)
		return choice

	def getPolicyMetrics(self):
		return []

	def train(self, task, job, device, cause=None):
		if not self.productionMode:
			debug.learnOut("Training: [{}] [{}] [{}]".format(task, job, device), 'y')
			self.systemState.updateState(task, job, device)

			if job.beforeState[0] == 4 and job.beforeState[1] == 0:
				print("training for", job, cause)
			if cause is None:
				traceback.print_stack()

			self.backward(job, episodeFinished=job.episodeFinished(), task=task, device=device)
			debug.infoOut("train: %s %s %s A %s R %.2f" % (task, job, device, self.possibleActions[job.latestAction], self.latestReward))
			debug.infoOut("to     %s %d" % (self.systemState.getStateDescription(), self.systemState.getIndex()))
			debug.infoOut("from   %s" % self.systemState.getStateDescription(self.systemState.getIndex(job.beforeState)))


	genericException = Exception("Not implemented in generic Q agent")
	def predict(self, state):
		raise self.genericException
	# def predictBatch(self, stateBatch):
	# 	raise self.genericException
	def createModel(self):
		raise self.genericException

	def trainModel(self, latestAction, R, beforeState, afterState, finished):
		raise self.genericException



	def saveModel(self):
		raise self.genericException


	def loadModel(self):
		raise self.genericException
