from learning.action import LOCAL
from offloading.offloadingDecision import offloadingDecision


class local(offloadingDecision):
	def setOptions(self, allDevices):
		offloadingDecision.options = [self.owner]

	def chooseDestination(self, task, job, device):
		choice = LOCAL
		choice.updateTargetDevice(self.owner, [self.owner])
