from sim import debug
from sim.learning.state.discretisedSystemState import discretisedSystemState, discreteState
from sim.simulations import constants


class targetedSystemState(discretisedSystemState):

	def __init__(self, numDevices, maxJobs, numTasks, allowExpansion=constants.ALLOW_EXPANSION):
		self.maxJobs = maxJobs
		# add extra state for "full" job queue
		if allowExpansion:
			singles = [discreteState('energyRemaining', 5),
					   discreteState('jobsInQueue', maxJobs + 1),
					   discreteState('currentConfig', 2, scale=False),
					   discreteState('taskId', numTasks)]
		else:
			singles = [ discreteState('currentConfig', 2, scale=False),
						discreteState('energyRemaining', 5),
					   	discreteState('jobsInQueue', maxJobs + 1),
						discreteState('taskId', numTasks)]
		multiples = []

		args = discretisedSystemState.convertTuples(numDevices=numDevices, singlesWithDiscreteNum=singles, multiplesWithDiscreteNum=multiples)
		discretisedSystemState.__init__(self, *args)

	def updateState(self, task, job, device):
		debug.out(debug.formatDebug("update state: %s %s %d %s %s", (device, device.batchLength(task), device.maxJobs, task, job)))
		self.setField('jobsInQueue', device.batchLength(task) / device.maxJobs)
		self.setField('currentConfig', device.fpga.isConfigured(task))
		# print("set currentconfig", device.fpga.isConfigured(task), task, device.getFpgaConfiguration())
		self.setField('energyRemaining', device.getEnergyLevelPercentage())
		self.setField('taskId', task.identifier)

		# print(self.currentState)
		# print("taskId", self.getField('taskId'))
		# print("energy", device.getEnergyLevelPercentage(), self.getField('energyRemaining'))

	def fromSystemState(self):
		# TODO: actually should overwrite this for each subclass
		second = self.__class__(self.numDevices, self.maxJobs)

		second.setState(self.currentState)

		return second
