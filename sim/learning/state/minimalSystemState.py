from sim import debug
from sim.learning.state.discretisedSystemState import discretisedSystemState, discreteState
from sim.simulations import constants


class minimalSystemState(discretisedSystemState):

	def __init__(self, simulation):
		# add extra state for "full" job queue
		singles = [discreteState('energyRemaining', 3), discreteState('jobsInQueue', constants.MAX_JOBS + 1, scalingFactor=constants.MAX_JOBS),
				   discreteState('currentConfig', 2, scale=False)]
		multiples = []

		discretisedSystemState.__init__(self, simulation, singlesWithDiscreteNum=singles, multiplesWithDiscreteNum=multiples)

	# def updateSystem(self):
	# 	pass
	def updateState(self, task, job, device):
		debug.learnOut("update state: %s %s %d %s %s" % (device, device.batchLength(task), constants.MAX_JOBS, task, job))
		self.setField('jobsInQueue', device.batchLength(task) / constants.MAX_JOBS)
		self.setField('currentConfig', device.fpga.getCurrentConfigIndex())
		self.setField('energyRemaining', device.getEnergyLevelPercentage())

	# def updateJob(self, job):
	# 	pass
	#
	# def updateTask(self, task):
	# 	pass