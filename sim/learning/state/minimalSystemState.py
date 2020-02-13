from sim.learning.state.discretisedSystemState import discretisedSystemState
from sim.simulations import constants

singles = [('jobsInQueue', constants.MAX_JOBS), ('currentConfig', 2), ('energyRemaining', 3)]
multiples = []

class minimalSystemState(discretisedSystemState):

	def __init__(self, simulation):
		discretisedSystemState.__init__(self, simulation, singlesWithBitwidths=singles, multiplesWithBitwidths=multiples)

	# def updateSystem(self):
	# 	pass
	def updateState(self, task, job, device):
		self.setField('jobsInQueue', device.batchLength(task) / constants.MAX_JOBS)
		self.setField('currentConfig', device.fpga.getCurrentConfigIndex())
		self.setField('energyRemaining', device.getEnergyLevelPercentage())
		print("setting energy to", self.getField('energyRemaining'), device.energyLevel, device.maxEnergyLevel)

	# def updateJob(self, job):
	# 	pass
	#
	# def updateTask(self, task):
	# 	pass