import sys

import sim.debug as debug
import sim.simulations.constants as constants
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.localAgent import localAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.randomAgent import randomAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.offloading.offloadingPolicy import *
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation

if __name__ == '__main__':
	print("testing simple simulation")
	debug.enabled = True
	debug.learnEnabled = True
	constants.DRAW_DEVICES = False
	exp = Simulation(numDevices=1, maxJobs=1, systemStateClass=minimalSystemState, agentClass=lazyAgent, offPolicy=True)
	exp.setBatterySize(1e1)
	print("Using target model:", exp.sharedAgent.offPolicy)

	# for i in range(10):
	# 	exp.simulateTick()
	exp.sharedAgent.printModel()
	exp.sharedAgent.printTargetModel()

	print("EPISODE")
	exp.simulateEpisode()
	# for i in range(1):
	# 	exp.simulateUntilJobDone()
