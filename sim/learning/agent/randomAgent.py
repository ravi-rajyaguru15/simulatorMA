from sim.learning.action import offloading, LOCAL, BATCH
from sim.learning.agent.staticAgent import staticAgent


class randomAgent(staticAgent):
	def setOptions(self, allDevices):
		self.options = allDevices

	def setDevices(self, devices):
		# local options are only available
		self.possibleActions = [offloading(i) for i in range(len(devices))] + [BATCH, LOCAL]
		for i in range(len(self.possibleActions)):
			self.possibleActions[i].index = i
		print('actions', self.possibleActions)
		# self.numActionsPerDevice = len(self.possibleActions)

		self.numOptions = len(self.possibleActions)

		# needs numActions
		self.createModel()

		self.devices = devices
		# return self.possibleActions