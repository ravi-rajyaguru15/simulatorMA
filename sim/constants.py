import sim.tasks
from sim.variable import *
import sim.powerPolicy
import sim.offloadingPolicy
from enum import Enum

# node types
ELASTIC_NODE = 0
END_DEVICE = 1
SERVER = 2

# current usage in mA
WIRELESS_RX_CURRENT = Gaussian(20., 1.) #
WIRELESS_TX_CURRENT = Gaussian(20., 1.) #
WIRELESS_IDLE_CURRENT = Gaussian(5, 1)
WIRELESS_SLEEP_CURRENT = Constant(0)

MCU_ACTIVE_CURRENT = Gaussian(12, .25)
MCU_IDLE_CURRENT = Gaussian(.5, 0.1) #
MCU_SLEEP_CURRENT = Gaussian(0.25, 0.1)

FPGA_ACTIVE_INT_CURRENT = Gaussian(13.5, 1.)
FPGA_IDLE_INT_CURRENT = Gaussian(13, 1.)
FPGA_SLEEP_INT_CURRENT = Constant(0)
FPGA_RECONFIGURATION_INT_CURRENT = Gaussian(10., 1.)
FPGA_ACTIVE_AUX_CURRENT = Gaussian(8.5, .5)
FPGA_IDLE_AUX_CURRENT = Gaussian(8, 1.)
FPGA_SLEEP_AUX_CURRENT = Constant(0)
FPGA_RECONFIGURATION_AUX_CURRENT = Gaussian(100., 5.)

# speeds in kB/s
WIRELESS_SPEED = Constant(250/8.) #
ETHERNET_SPEED = Gaussian(500. * 1024., 50.) #
MCU_F = 8e6
MCU_PROCESSING_SPEED = Constant(MCU_F)
FPGA_F = 32e6
FPGA_PROCESSING_SPEED = Constant(FPGA_F/10) # 32 MHz * 10 neurons
SERVER_PROCESSING_SPEED = Constant(1000./8./16*3000) # mcu * 3GHz / 16MHz
MCU_FPGA_COMMUNICATION_SPEED = Constant(MCU_F/4) # 4cl * 8MHz

# time in s
MCU_BATCHING_LATENCY = Gaussian(20e-3, 5e-3)
MCU_MW_OVERHEAD_LATENCY = Gaussian(20e-3, 5e-3)
MCU_MESSAGE_OVERHEAD_LATENCY = Gaussian(5e-3, 1e-3) #
SERVER_MESSAGE_OVERHEAD_LATENCY = Gaussian(1e-4, 1.1e-4) #
ETHERNET_PING = Gaussian(5. / 1000., 15. / 1000.) #

# voltage in V
MCU_VOLTAGE = Constant(3.3) #
FPGA_INT_VOLTAGE = Constant(1.2) #
FPGA_AUX_VOLTAGE = MCU_VOLTAGE
WIRELESS_VOLTAGE = Constant(3.3)

# size in bytes
SAMPLE_SIZE = Uniform(1, 11, integer=True)
SAMPLE_RAW_SIZE = Constant(400, integer=True) # FRAGMENTATION
SAMPLE_PROCESSED_SIZE = Constant(100, integer=True) #

# time
SIM_TIME = 2e-2
TD = 1e-3
PLOT_TD = 1e-3
uni = Uniform(0, 1)
JOB_LIKELIHOOD = 1e-3
RECONFIGURATION_TIME = Constant(0.1)

# offloading
OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
OFFLOADING_PEER = 0

# energy management
FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF # TODO: entirely unimplemented, sleep current and timer for sleep
MCU_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF # TODO: entirely unimplemented, sleep current and timer for sleep
FPGA_IDLE_SLEEP = 0.1
MCU_IDLE_SLEEP = .05

# batching policy
MINIMUM_BATCH = 5

# tasks
DEFAULT_TASK_GRAPH = [sim.tasks.EASY] # TODO: single task only

# visualisation
DRAW_DEVICES = True
DRAW_GRAPH_TOTAL_ENERGY = False
DRAW_GRAPH_CURRENT_POWER = False
DRAW = True
SAVE = False
DRAW_GRAPH = True
SAVE_GRAPH = False

# def randomise(range):
# 	return random.uniform(range[0], range[1])

# experiments
REPEATS = 4
THREAD_COUNT = 14
MAX_DELAY = 0.1