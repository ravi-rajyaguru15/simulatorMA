from sim import debug
from sim.learning.action import OFFLOADING
from sim.learning.agent.agent import agent
import numpy as np

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

	def forward(self, task, job, device):
		if not device.hasOffloadingOptions() and OFFLOADING in self.possibleActions:
			assert self.possibleActions[0] is OFFLOADING
			actionIndex = np.random.randint(1, self.numActions - 1)
			debug.out("no offloading available")
		else:
			if len(device.offloadingOptions) == 0:
				print("no offloading options", device.offloadingOptions, device.agent.devices)
			actionIndex = self.selectAction(job.beforeState)

		choice = self.possibleActions[actionIndex]
		choice.updateTargetDevice(owner=device, offloadingDevices=device.offloadingOptions)
		return choice

# def setReconsiderBatches(self, reconsiderBatches): pass
