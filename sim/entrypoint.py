#!/usr/bin/env python3

import os
import sys


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# print (sys.path)
sys.path.insert(0, '.')

# from sim.experiments.transient import agentJobNumber, testRewards
import sim.test.testMultiTask

import glob

# import sim
# import sim.experiments.expectedLife
import sim.simulations.constants

if __name__ == '__main__':

	from sim.simulations import localConstants
	print(glob.glob(localConstants.OUTPUT_DIRECTORY))
	print("cores:", sim.simulations.constants.THREAD_COUNT)
	if sim.simulations.constants.THREAD_COUNT > 64:
		sim.simulations.constants.THREAD_COUNT = 64
	print(localConstants.OUTPUT_DIRECTORY)

	import sim.test.testLearning

	# from sim.experiments.acsos2020.experiment1 import run
	# # run(2e3)
	# localConstants.REPEATS = 128
	# run(1e6)


# agentJobNumber.run(1e6)
# testRewards.run()

# sim.simulations.constants.DRAW_GRAPH = False
# sim.simulations.constants.SAVE_GRAPH = True
# sim.simulations.constants.TOTAL_TIME = 1e4

# import sim.experiments.offloadingPolicies
# import sim.experiments.roundRobin
# print(sim.constants.THREAD_COUNT)
# sim.experiments.expectedLife.run()

# import subprocess
# subprocess.run(["/usr/local/bin/syncSciebo"])
