# check resulting job energy based on system state
import sim
from sim import debug
from sim.devices.platforms.platform import elasticNodev4
from sim.offloading import offloadingPolicy
from sim.simulations import constants
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation

if __name__ == "__main__":
	constants.OFFLOADING_POLICY = offloadingPolicy.REINFORCEMENT_LEARNING
	constants.NUM_DEVICES = 1
	elasticNodev4.BATTERY_SIZE = 1e-3
	debug.enabled = True
	exp = Simulation()

	exp.simulate()

	# simulations done
	jobsList = exp.finishedJobsList + exp.unfinishedJobsList

	# for i in range(10):
	# 	exp.simulateUntilJobDone()
	for job in jobsList:
		beforeState = job.beforeState
		energyCost = job.totalEnergyCost * 1e3
		print("%s %s created: %.2f energy: %.4f %s" % (job, job.finished, job.createdTime, energyCost, beforeState.dictRepresentation))
