import sys

import numpy as np

import sim
import sim.debug as debug
# from sim.learning.state.binarySystemState import binarySystemState
from sim.learning.state.minimalAgent import minimalAgent
from sim.learning.state.minimalSystemState import minimalSystemState
import sim.simulations.constants as constants
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation
from sim.offloading.offloadingPolicy import *
from sim.learning.offloadingDecision import offloadingDecision

if __name__ == '__main__':
	print("testing simple simulation")
	constants.NUM_DEVICES = 1
	constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e1
	constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
	debug.enabled = False
	constants.DRAW_DEVICES = False
	exp = Simulation(minimalSystemState, offloadingDecision, minimalAgent)

	# for i in range(1000):
	i = 0
	# while exp.getCompletedJobs() < 10000:
	# 	debug.out("\ntick %d" % i)
	# 	i+=1
	# 	exp.simulateTick()
	exp.simulateEpisode()

	print("Experiment done!", exp.time)

	np.set_printoptions(threshold=sys.maxsize, suppress=True)
	sim.learning.offloadingDecision.sharedAgent.printModel()
