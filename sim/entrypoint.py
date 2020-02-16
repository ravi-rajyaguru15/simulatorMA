#!/usr/bin/env python3

import os
import sys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
print (sys.path)
sys.path.insert(0, '.')

import glob
print(glob.glob("/output/*.*"))

# import sim 
# import sim.experiments.expectedLife
import sim.simulations.constants

print("cores:", sim.simulations.constants.THREAD_COUNT)

sim.simulations.constants.DRAW_GRAPH = False
sim.simulations.constants.SAVE_GRAPH = True
sim.simulations.constants.TOTAL_TIME = 1e4

# import sim.experiments.offloadingPolicies
# import sim.experiments.roundRobin
# print(sim.constants.THREAD_COUNT)
# sim.experiments.expectedLife.run()

# import subprocess
# subprocess.run(["/usr/local/bin/syncSciebo"])
