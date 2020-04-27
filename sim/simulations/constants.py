import multiprocessing
import os

import sim.devices.components.powerPolicy
import sim.devices.platforms.platform
import sim.offloading.offloadingPolicy
import sim.tasks.tasks
from sim.simulations.variable import *

# node types
DEFAULT_ELASTIC_NODE = sim.devices.platforms.platform.elasticNodev4

# size in bytes
SAMPLE_SIZE = Uniform(5, 10, integer=True)

# time
TOTAL_TIME = 1e1
SIM_TIME = 2e-2
TD = 1e-3
PLOT_SKIP = 1e1
uni = Uniform(0.5, 1)
JOB_LIKELIHOOD = 1e-3 # used in td simulations
DEFAULT_TIME_INTERVAL = 1
JOB_INTERVAL = Gaussian(DEFAULT_TIME_INTERVAL, 1e-0) # used in simple simulations

# offloading
# OFFLOADING_POLICY = sim.offloading.offloadingPolicy.REINFORCEMENT_LEARNING
OFFLOADING_PEER = 0
ROUND_ROBIN_TIMEOUT = 2

# learning
CENTRALISED_LEARNING = True
LEARNING_RATE = 1e-1
GAMMA = 1e-3
EPS = 0.1
EPS_DECAY = True
EPS_MIN = 0.1
EPS_MAX = 1.
EPS_STEP_COUNT = 1000
EXPECTED_LIFETIME_ALPHA = 0.1
GRACEFUL_FAILURE_LEVEL = 0.1
ALLOW_EXPANSION = False
INITIAL_Q = 25.
OFF_POLICY = False

# energy management
FPGA_POWER_PLAN = sim.devices.components.powerPolicy.IDLE_TIMEOUT
MCU_POWER_PLAN = sim.devices.components.powerPolicy.IMMEDIATELY_OFF
FPGA_IDLE_SLEEP = 1e-1
MCU_IDLE_SLEEP = .05

# batching policy
# MINIMUM_BATCH = 5
MAX_JOBS = 3
ABSOLUTE_MAX_JOBS = 15

# tasks
DEFAULT_TASK_GRAPH = [sim.tasks.tasks.EASY] # TODO: single task only
MAXIMUM_TASK_QUEUE = 5

# visualisation
DRAW_DEVICES = False
DRAW_GRAPH_TOTAL_ENERGY = False
DRAW_GRAPH_CURRENT_POWER = False
DRAW_GRAPH_SUBTASK_DURATION = False
DRAW_GRAPH_EXPECTED_LIFETIME = False
# DRAW = True
# SAVE = False
# DRAW_GRAPH = True
# SAVE_GRAPH = False

# RECONSIDER_BATCHES = False

# experiments
NUM_DEVICES = 2
# REPEATS = 4
THREAD_COUNT = multiprocessing.cpu_count()
MAX_DELAY = 0.1

