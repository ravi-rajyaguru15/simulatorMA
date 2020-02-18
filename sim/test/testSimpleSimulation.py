import sys
import traceback
import numpy as np

import sim
import sim.debug as debug
import sim.simulations.constants as constants
from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.offloadingDecision import offloadingDecision as offloadingDecisionClass
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

	# while True:
	if True:
	# for i in range(100):
	# i = 0
	# while exp.getCompletedJobs() < 10000:
	# 	debug.out("\ntick %d" % i)
	# 	i+=1
	# 	exp.simulateTick()
		try:
			exp.simulateEpisode()
			print("Experiment done!", exp.time)
		except Exception:
			print("number of successful episodes:", exp.episodeNumber)
			print(sys.exc_info())
			# traceback.print_stack()
		# print("end of episode!", exp.time)


	# np.set_printoptions(threshold=sys.maxsize, suppress=True)
	# sim.learning.offloadingDecision.sharedAgent.printModel()
