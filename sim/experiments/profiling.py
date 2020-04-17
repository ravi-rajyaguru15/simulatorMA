# import pycallgraph.PyCallGraph
# import pycallgraph.output.GraphvizOutput

import cProfile

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

from sim import debug
from sim.devices.components.powerPolicy import IDLE_TIMEOUT
from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.offloading.offloadingDecision import offloadingDecision
from sim.offloading.offloadingPolicy import REINFORCEMENT_LEARNING
from sim.simulations import constants, localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation
from sim.simulations.variable import Constant
from sim.tasks.tasks import EASY


def profileTarget():
	debug.settings.enabled = False
	debug.settings.learnEnabled = False

	exp = Simulation(numDevices=4, systemStateClass=minimalSystemState, agentClass=minimalTableAgent)
	exp.setBatterySize(1e-1)
	for i in range(100):
		exp.simulateEpisode()

def testPerformance():
	# import os
	# cwd = os.getcwd()
	# print(cwd)
	profileFilename = localConstants.OUTPUT_DIRECTORY + '/profileResults.prof'
	open(profileFilename, 'wb')
	cProfile.run('profileTarget()', filename=profileFilename, sort='cumtime')


debug.settings.fileOutput = False
localConstants.DEBUG_HISTORY = False
testPerformance()
print("done")
# graphviz = GraphvizOutput()
# graphviz.output_file = localConstants.OUTPUT_DIRECTORY + 'profile.png'
#
# with PyCallGraph(output=GraphvizOutput()):
# # if True:
# 	profileTarget()