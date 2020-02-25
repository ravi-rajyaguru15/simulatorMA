from sim import debug
from sim.learning.state.discretisedSystemState import discretisedSystemState, discreteState
from sim.simulations import constants


class minimalSystemState(discretisedSystemState):
	maxJobs = None

	def __init__(self, simulation, numDevices, maxJobs):
		self.maxJobs = maxJobs
		# add extra state for "full" job queue
		singles = [discreteState('energyRemaining', 3), discreteState('jobsInQueue', maxJobs + 1, scalingFactor=maxJobs),
				   discreteState('currentConfig', 2, scale=False)]
		multiples = []

		discretisedSystemState.__init__(self, simulation, numDevices=numDevices, singlesWithDiscreteNum=singles, multiplesWithDiscreteNum=multiples)

	# def updateSystem(self):
	# 	pass
	def updateState(self, task, job, device):
		debug.learnOut("update state: %s %s %d %s %s" % (device, device.batchLength(task), device.maxJobs, task, job))
		self.setField('jobsInQueue', device.batchLength(task) / device.maxJobs)
		self.setField('currentConfig', device.fpga.getCurrentConfigIndex())
		self.setField('energyRemaining', device.getEnergyLevelPercentage())

	def fromSystemState(self, simulation):
		# TODO: actually should overwrite this for each subclass
		second = self.__class__(simulation, self.numDevices, self.maxJobs)

		second.setState(self.currentState)

		# second.dictRepresentation = systemState.createDictionaryRepresentation(second.currentState)
		return second

	# def updateJob(self, job):
	# 	pass
	#
	# def updateTask(self, task):
	# 	pass