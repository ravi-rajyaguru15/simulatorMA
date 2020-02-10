# import pycallgraph.PyCallGraph
# import pycallgraph.output.GraphvizOutput

import cProfile

from sim import debug
from sim.devices.components.powerPolicy import IDLE_TIMEOUT
from sim.offloading.offloadingPolicy import REINFORCEMENT_LEARNING
from sim.simulations import constants
from sim.simulations.variable import Constant
from sim.tasks.tasks import EASY
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation


def profileTarget():
	debug.enabled = True
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
	constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e-2

	exp = Simulation(hardwareAccelerated=True)
	exp.simulateEpisode()
	# exp.simulateTime(10)

def testPerformance():
	cProfile.run('profileTarget()', filename='profileResults.prof', sort='cumtime')

testPerformance()
# graphviz = GraphvizOutput()
# graphviz.output_file = 'profile.png'

# with PyCallGraph(output=GraphvizOutput()):
# # if True:
# 	profileTarget()