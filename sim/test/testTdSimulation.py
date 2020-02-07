import sim.debug as debug
import sim.simulations.constants as constants
import sim.simulations as simulations
from sim.simulations.TdSimulation import TdSimulation as Simulation
from sim.offloading.offloadingPolicy import *

if __name__ == '__main__':
	print("testing simple simulation")
	constants.NUM_DEVICES = 2
	constants.OFFLOADING_POLICY = RANDOM_PEER_ONLY
	debug.enabled = True
	constants.DRAW_DEVICES = False
	simulations.current = Simulation()

	# for i in range(1000):
	i = 0
	while simulations.current.getCompletedJobs() < 1000:
		# debug.out("\ntick %d" % i)
		i+=1
		simulations.current.simulateTick()

	print("Experiment done!", simulations.current.time)
