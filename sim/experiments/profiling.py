# import pycallgraph.PyCallGraph
# import pycallgraph.output.GraphvizOutput

import cProfile

from learning.agent.minimalAgent import minimalAgent
from learning.offloadingDecision import offloadingDecision
from learning.state.minimalSystemState import minimalSystemState
from sim import debug
from sim.devices.components.powerPolicy import IDLE_TIMEOUT
from sim.offloading.offloadingPolicy import REINFORCEMENT_LEARNING
from sim.simulations import constants
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation
from sim.simulations.variable import Constant
from sim.tasks.tasks import EASY


def profileTarget():
	debug.enabled = False
	constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
	constants.JOB_LIKELIHOOD = 1e-3 # 2e-3
	constants.SAMPLE_RAW_SIZE = Constant(40)
	constants.SAMPLE_SIZE = Constant(10)
	constants.PLOT_TD = 10
	constants.FPGA_POWER_PLAN = IDLE_TIMEOUT
	constants.DRAW_DEVICES = False
	constants.FPGA_IDLE_SLEEP = 0.75
	constants.MINIMUM_BATCH = 5
	constants.DEFAULT_TASK_GRAPH = [EASY]
	constants.ROUND_ROBIN_TIMEOUT = 1e1
	constants.MEASUREMENT_NOISE = True
	constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e2
	constants.NUM_DEVICES = 1

	exp = Simulation(minimalSystemState, offloadingDecision, minimalAgent)
	exp.simulateEpisode()
	# exp.simulateTime(10)

def testPerformance():
	import os
	cwd = os.getcwd()
	print(cwd)
	profileFilename = '/tmp/profileResults.prof'
	open(profileFilename, 'wb')
	cProfile.run('profileTarget()', filename=profileFilename, sort='cumtime')

testPerformance()
# graphviz = GraphvizOutput()
# graphviz.output_file = 'profile.png'

# with PyCallGraph(output=GraphvizOutput()):
# # if True:
# 	profileTarget()