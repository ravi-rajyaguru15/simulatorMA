from sim import debug
from sim.learning.state.discretisedSystemState import discretisedSystemState, discreteState
from sim.simulations import constants


class minimalSystemState(discretisedSystemState):
	maxJobs = None

	def __init__(self, numDevices, maxJobs, allowExpansion=constants.ALLOW_EXPANSION):
		self.maxJobs = maxJobs
		# add extra state for "full" job queue
		if allowExpansion:
			singles = [discreteState('energyRemaining', 3),
					   discreteState('jobsInQueue', maxJobs + 1),
					   discreteState('currentConfig', 2, scale=False)]
		else:
			singles = [discreteState('energyRemaining', 3),
					   discreteState('jobsInQueue', maxJobs + 2, scalingFactor=maxJobs + 1),
					   discreteState('currentConfig', 2, scale=False)]
		multiples = []

		discretisedSystemState.__init__(self, *discretisedSystemState.convertTuples(numDevices=numDevices, singlesWithDiscreteNum=singles, multiplesWithDiscreteNum=multiples))
		# print("created from tuples", self, self.__class__, self.singlesDiscrete)

	# def updateSystem(self):
	# 	pass
	def updateState(self, task, job, device):
		debug.learnOut("update state: %s %s %d %s %s" % (device, device.batchLength(task), device.maxJobs, task, job))
		self.setField('jobsInQueue', device.batchLength(task) / device.maxJobs)
		self.setField('currentConfig', device.fpga.getCurrentConfigIndex())
		self.setField('energyRemaining', device.getEnergyLevelPercentage())

	def fromSystemState(self):
		# TODO: actually should overwrite this for each subclass
		second = self.__class__(self.numDevices, self.maxJobs)

		second.setState(self.currentState)

		# second.dictRepresentation = systemState.createDictionaryRepresentation(second.currentState)
		return second

	# def updateJob(self, job):
	# 	pass
	#
	# def updateTask(self, task):
	# 	pass