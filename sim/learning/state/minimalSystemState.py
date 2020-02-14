from sim.learning.state.discretisedSystemState import discretisedSystemState, discreteState
from sim.simulations import constants

singles = [discreteState('energyRemaining', 3), discreteState('jobsInQueue', constants.MAX_JOBS), discreteState('currentConfig', 2, scale=False)]
multiples = []

class minimalSystemState(discretisedSystemState):

	def __init__(self, simulation):
		discretisedSystemState.__init__(self, simulation, singlesWithDiscreteNum=singles, multiplesWithDiscreteNum=multiples)

	# def updateSystem(self):
	# 	pass
	def updateState(self, task, job, device):
		self.setField('jobsInQueue', device.batchLength(task) / constants.MAX_JOBS)
		self.setField('currentConfig', device.fpga.getCurrentConfigIndex())
		self.setField('energyRemaining', device.getEnergyLevelPercentage())

	# def updateJob(self, job):
	# 	pass
	#
	# def updateTask(self, task):
	# 	pass