import sys

import sim.debug as debug
import sim.simulations.constants as constants
from sim.learning.agent.minimalAgent import minimalAgent
from offloading.offloadingDecision import offloadingDecision as offloadingDecisionClass
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.offloading.offloadingPolicy import *
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation

if __name__ == '__main__':
	print("testing simple simulation")
	constants.NUM_DEVICES = 1
	constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e0
	constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
	debug.enabled = False
	constants.DRAW_DEVICES = False
	exp = Simulation(minimalSystemState, offloadingDecisionClass, minimalAgent)

	try:
		exp.simulateEpisode()
		print("Experiment done!", exp.time)
	except Exception:
		print("number of successful episodes:", exp.episodeNumber)
		print(sys.exc_info())
