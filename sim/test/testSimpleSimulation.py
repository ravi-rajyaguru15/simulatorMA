import sim
import sim.debug as debug
from sim.learning.state.binarySystemState import binarySystemState
import sim.simulations.constants as constants
import sim.simulations as simulations
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation
from sim.offloading.offloadingPolicy import *
from sim.learning.agent.qTableAgent import qTableAgent
from sim.learning.offloadingDecision import offloadingDecision

if __name__ == '__main__':
	print("testing simple simulation")
	constants.NUM_DEVICES = 1
	constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
	debug.enabled = False
	constants.DRAW_DEVICES = False
	exp =Simulation(binarySystemState, offloadingDecision, qTableAgent)
	# exp = sim.simulations.Simulation.currentSimulation

	# for i in range(1000):
	i = 0
	while exp.getCompletedJobs() < 10:
		debug.out("\ntick %d" % i)
		i+=1
		exp.simulateTick()

	print("Experiment done!", exp.time)
