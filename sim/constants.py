import sim.tasks
from sim.variable import *
import sim.powerPolicy
import sim.offloadingPolicy
from enum import Enum
import multiprocessing
import sim.platforms.platform

# node types
DEFAULT_ELASTIC_NODE = sim.platforms.platform.elasticNodev4

# size in bytes
SAMPLE_SIZE = Uniform(5, 10, integer=True)

# time
TOTAL_TIME = 1e1
SIM_TIME = 2e-2
TD = 1e-3
PLOT_TD = 1e-3
uni = Uniform(0.5, 1)
JOB_LIKELIHOOD = 1e-3

# offloading
OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
OFFLOADING_PEER = 0
ROUND_ROBIN_TIMEOUT = 2

# learning
CENTRALISED_LEARNING = True
LEARNING_RATE = 0.001
GAMMA = 1e-3
EPS = 0.1
EPS_MIN = 0.1
EPS_MAX = 1.
EPS_STEP_COUNT = 1000

# energy management
FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
MCU_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF
FPGA_IDLE_SLEEP = 0.5
MCU_IDLE_SLEEP = .05

# batching policy
MINIMUM_BATCH = 5

# tasks
DEFAULT_TASK_GRAPH = [sim.tasks.EASY] # TODO: single task only
MAXIMUM_TASK_QUEUE = 5

# visualisation
DRAW_DEVICES = False
DRAW_GRAPH_TOTAL_ENERGY = False
DRAW_GRAPH_CURRENT_POWER = False
DRAW_GRAPH_SUBTASK_DURATION = False
DRAW_GRAPH_EXPECTED_LIFETIME = False
# DRAW = True
# SAVE = False
DRAW_GRAPH = True
SAVE_GRAPH = False

# def randomise(range):
# 	return random.uniform(range[0], range[1])

# experiments
NUM_DEVICES = 2
REPEATS = 4
THREAD_COUNT = multiprocessing.cpu_count()
MAX_DELAY = 0.1
EXPECTED_LIFETIME_ALPHA = 0.1
MEASUREMENT_NOISE = True