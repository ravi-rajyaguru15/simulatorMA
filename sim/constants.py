import sim.tasks
from sim.variable import *
import sim.powerPolicy
import sim.offloadingPolicy
from enum import Enum
import multiprocessing
import sim.platforms.elasticNodev4

# node types
DEFAULT_ELASTIC_NODE = sim.platforms.elasticNodev4
# ELASTIC_NODE_V4 = 0
# ELASTIC_NODE = 0
# END_DEVICE = 1
# SERVER = 2

# size in bytes
SAMPLE_SIZE = Uniform(1, 11, integer=True)

# time
TOTAL_TIME = 1e1
SIM_TIME = 2e-2
TD = 1e-3
PLOT_TD = 1e-3
uni = Uniform(0, 1)
JOB_LIKELIHOOD = 1e-3

# offloading
OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
OFFLOADING_PEER = 0
ROUND_ROBIN_TIMEOUT = 2

# energy management
FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF # TODO: entirely unimplemented, sleep current and timer for sleep
MCU_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF # TODO: entirely unimplemented, sleep current and timer for sleep
FPGA_IDLE_SLEEP = 0.1
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
# DRAW = True
# SAVE = False
DRAW_GRAPH = True
SAVE_GRAPH = False

# def randomise(range):
# 	return random.uniform(range[0], range[1])

# experiments
REPEATS = 4
THREAD_COUNT = multiprocessing.cpu_count()
MAX_DELAY = 0.1