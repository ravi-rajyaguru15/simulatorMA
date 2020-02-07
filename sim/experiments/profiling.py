# import pycallgraph.PyCallGraph
# import pycallgraph.output.GraphvizOutput

import cProfile
from sim.simulation import simulation
import sim.simulation
import sim.tasks.tasks
import sim.simulations.variable
import sim.offloading.offloadingPolicy
import sim.devices.components.powerPolicy
import sim.platforms

def profileTarget():
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = sim.offloading.offloadingPolicy.REINFORCEMENT_LEARNING
	sim.constants.JOB_LIKELIHOOD = 1e-3 # 2e-3
	sim.constants.SAMPLE_RAW_SIZE = sim.simulations.variable.Constant(40)
	sim.constants.SAMPLE_SIZE = sim.simulations.variable.Constant(10)
	sim.constants.PLOT_TD = 10
	sim.constants.FPGA_POWER_PLAN = sim.devices.components.powerPolicy.IDLE_TIMEOUT
	sim.constants.DRAW_DEVICES = False
	sim.constants.FPGA_IDLE_SLEEP = 0.75
	sim.constants.MINIMUM_BATCH = 5
	sim.constants.DEFAULT_TASK_GRAPH = [sim.tasks.tasks.EASY]
	sim.constants.ROUND_ROBIN_TIMEOUT = 1e1
	sim.constants.MEASUREMENT_NOISE = True
	sim.constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1

	exp = simulation(hardwareAccelerated=True)
	sim.simulations.current = exp
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