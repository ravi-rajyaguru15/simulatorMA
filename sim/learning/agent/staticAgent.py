from sim.learning.agent.agent import agent


# this class is for all agent types that don't learn
class staticAgent(agent):
	def trainModel(self, latestAction, R, beforeState, afterState, finished):
		pass

	def createModel(self):
		pass

	def backward(self, job):
		pass

	def train(self, task, job, device, cause=None):
		pass

	def updateTargetModel(self):
		pass