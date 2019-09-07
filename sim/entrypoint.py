#!/usr/bin/env python3

import numpy as np
import random
import matplotlib.pyplot as pp
import sys
import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
print (sys.path)
sys.path.insert(0, '/app')
import rl.agents
import rl.memory
import keras
import keras.utils



# import sim 
import sim.experiments.expectedLife
import sim.constants

sim.constants.DRAW_GRAPH = False
sim.constants.SAVE_GRAPH = True

print(sim.constants.THREAD_COUNT)
# import tictactoe
# sim.experiments.expectedLife.run()