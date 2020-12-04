# import pycallgraph.PyCallGraph
# import pycallgraph.output.GraphvizOutput

import cProfile

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

from sim import debug
from sim.devices.components.powerPolicy import IDLE_TIMEOUT
from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.minimalDeepAgent import minimalDeepAgent
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

	exp = Simulation(numDevices=2, systemStateClass=minimalSystemState, agentClass=minimalDeepAgent, centralisedLearning=True, offPolicy=True, trainClassification=False)
	exp.setBatterySize(1e-1)
	for i in range(1):
		exp.simulateEpisode(i)

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