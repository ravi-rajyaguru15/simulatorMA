from sim.learning.agent.agent import agent


class qAgent(agent):
	def reward(self, job):
		# default reward behaviour
		jobReward = 1 if job.finished else 0
		deadlineReward = 0 if job.deadlineMet() else -0.5
		expectedLifetimeReward = -.5 if (job.startExpectedLifetime - job.systemLifetime()) > (
					job.currentTime - job.createdTime) else 0  # reward if not reducing lifetime more than actual duration
		simulationDoneReward = -100 if job.episodeFinished() else 0

		sim.debug.learnOut(
			'reward: job {} deadline {} expectedLife {} simulationDone {}'.format(jobReward, deadlineReward,
																				  expectedLifetimeReward,
																				  simulationDoneReward), 'b')
		# traceback.print_stack()

		return jobReward + deadlineReward + expectedLifetimeReward + simulationDoneReward

	# update based on resulting system state and reward
	def backward(self, job):
		reward = self.reward(job)
		finished = job.episodeFinished()

		sim.debug.learnOut("backward {} {}".format(reward, finished), 'y')
		sim.debug.learnOut("\n")
		# traceback.print_stack()
		# sim.debug.learnOut("\n")

		self.totalReward += reward
		self.episodeReward += reward

		sim.counters.NUM_BACKWARD += 1

		# update model here
		self.trainModel(job.latestAction, reward, job.beforeState, self.systemState, finished)

		# new metrics
		self.latestReward = reward
		# self.latestR = R

		# sim.debug.learnOut\
		diff = self.systemState - job.beforeState
		np.set_printoptions(precision=3)
		# sim.debug.infoOut("{}, created: {:6.3f} {:<7}: {}, deadline: {:9.5f} ({:10.5f}), action: {:<9}, expectedLife (before: {:9.5f} - after: {:9.5f}) = {:10.5f}, reward: {}".format(job.currentTime, job.createdTime, str(job), int(job.finished), job.deadlineRemaining(), (job.currentTime - job.createdTime), str(self.possibleActions[job.latestAction]), job.beforeState.	getField("selfExpectedLife")[0], self.systemState.getField("selfExpectedLife")[0], diff["selfExpectedLife"][0], reward))
		# print("state diff: {}".format(diff).replace("array", ""), 'p')

		# save to history
		job.addToHistory(self.latestReward, self.latestMeanQ, self.latestLoss)

		# # metrics history
		# self.history.add("loss", self.loss)
		# self.history["reward"].append(self.latestReward)
		# self.history["q"].append(self.latestMeanQ)

		# print('reward', reward)

		sim.debug.learnOut("loss: {} reward: {}".format(self.latestLoss, self.latestReward), 'r')
		# sim.debug.learnOut("loss: {} reward: {} R: {}".format(self.latestLoss, self.latestReward, self.latestR), 'r')
	#
	# agent.step += 1
	# agent.update_target_model_hard()

	# return metrics

	def getPolicyMetrics(self):
		return []

	def train(self, task, job, device):
		sim.debug.learnOut("Training: [{}] [{}] [{}]".format(task, job, device), 'y')
		self.systemState.updateState(task, job, device)
		self.backward(job)


	genericException = Exception("Not implemented in generic Q agent")
	def predict(self, state):
		raise self.genericException
	# def predictBatch(self, stateBatch):
	# 	raise self.genericException
	def createModel(self):
		raise self.genericException

	def trainModel(self, latestAction, R, beforeState, afterState, finished):
		raise self.genericException
