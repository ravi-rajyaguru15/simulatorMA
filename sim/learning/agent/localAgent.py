from sim.learning.action import LOCAL, BATCH
from sim.learning.agent.staticAgent import staticAgent


class localAgent(staticAgent):
	__name__ = "Local Agent"
	# def setOptions(self, allDevices):
	# 	self.options = [self.owner]
	#
	# def chooseDestination(self, task, job, device):
	# 	choice = LOCAL
	# 	choice.updateTargetDevice(self.owner, [self.owner])
	# 	return choice

	def getOffloadingTargets(self, devices):
		return []

	def setDevices(self, devices):
		# local options are only available
		self.possibleActions = [BATCH, LOCAL]
		for i in range(len(self.possibleActions)):
			self.possibleActions[i].index = i
		print('actions', self.possibleActions)
		# self.numActionsPerDevice = len(self.possibleActions)

		# self.numOptions = len(self.possibleActions)

		# needs numActions
		self.createModel()

		self.devices = devices
		self._setDecisions(devices)
		# return self.possibleActions
