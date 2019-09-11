#!/usr/bin/env python3

import numpy as np
import random
import matplotlib.pyplot as pp
import sys
import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
print (sys.path)
sys.path.insert(0, '.')
import rl.agents
import rl.memory
import keras
import keras.utils

import glob
print(glob.glob("/output/*.*"))

# import sim 
# import sim.experiments.expectedLife
import sim.constants

print("cores:", sim.constants.THREAD_COUNT)

sim.constants.DRAW_GRAPH = False
sim.constants.SAVE_GRAPH = True

import sim.experiments.offloadingPolicies
# import sim.experiments.roundRobin
# print(sim.constants.THREAD_COUNT)
# import sim.tictactoe
# sim.experiments.expectedLife.run()