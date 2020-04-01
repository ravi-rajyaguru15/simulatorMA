import sys

import sim.debug as debug
import sim.simulations.constants as constants
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.localAgent import localAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.randomAgent import randomAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.offloading.offloadingPolicy import *
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation

if __name__ == '__main__':
	print("testing simple simulation")
	constants.NUM_DEVICES = 2
	constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e2
	constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
	debug.enabled = True
	debug.learnEnabled = True
	constants.DRAW_DEVICES = False
	exp = Simulation(numDevices=1, systemStateClass=minimalSystemState, agentClass=lazyTableAgent)

	# for i in range(10):
	# 	exp.simulateTick()

	for i in range(1):
		exp.simulateUntilJobDone()

	# exp.simulateUntilTime(50)

	# exp.simulateEpisode()

	# try:
	# 	exp.simulateEpisode()
	# 	print("Experiment done!", exp.time)
	# except Exception:
	# 	print("number of successful episodes:", exp.episodeNumber)
	# 	print(sys.exc_info())
