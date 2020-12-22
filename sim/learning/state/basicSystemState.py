from sim import debug
from sim.learning.state.discretisedSystemState import discretisedSystemState, discreteState
from sim.simulations import constants

import sys

#similar to minimalSystemState but not scaled

class basicSystemState(discretisedSystemState):
	maxJobs = None

	def __init__(self, numDevices, maxJobs, allowExpansion=constants.ALLOW_EXPANSION, numTasks=None, numEnergyLevels=constants.NUM_ENERGY_LEVELS):
		self.maxJobs = maxJobs

		# add extra state for "full" job queue
		singles = [ discreteState('energyRemaining', numEnergyLevels, scale=False), discreteState('jobsInQueue', maxJobs, scale=False)]
		multiples = []

		args = discretisedSystemState.convertTuples(numDevices=numDevices, singlesWithDiscreteNum=singles, multiplesWithDiscreteNum=multiples)
		# print("discrete:", args)
		discretisedSystemState.__init__(self, *args)

	def updateState(self, task, job, device):
		debug.out("update state: %s %s %d %s %s" % (device, device.batchLength(task), device.maxJobs, task, job))
		self.setField('jobsInQueue', device.batchLength(task), overrideScaling=True)
		self.setField('energyRemaining', device.getEnergyLevelPercentage(), overrideScaling=True)
		# print("energy", device.getEnergyLevelPercentage(), self.getField('energyRemaining'))

		# print("updateState", self.currentState)

	def fromSystemState(self):
		# TODO: actually should overwrite this for each subclass
		second = self.__class__(self.numDevices, self.maxJobs)
		second.setState(self.currentState)

		return second
