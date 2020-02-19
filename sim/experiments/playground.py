import multiprocessing

import sim
from sim import debug
from sim.devices.components import powerPolicy
from sim.offloading import offloadingPolicy
from sim.simulations import constants, variable
from sim.simulations.SimpleSimulation import SimpleSimulation

debug.enabled = True
constants.DRAW = False
constants.SAMPLE_SIZE = variable.Gaussian(10, 2)
constants.SAMPLE_RAW_SIZE = variable.Constant(4, integer=True)
constants.SAMPLE_PROCESSED_SIZE = variable.Constant(4, integer=True)
constants.FPGA_POWER_PLAN = powerPolicy.IDLE_TIMEOUT
constants.OFFLOADING_POLICY = offloadingPolicy.ANYTHING

processes = list()
constants.MINIMUM_BATCH = 5

# offloadingOptions = [True, False]
results = multiprocessing.Queue()
finished = multiprocessing.Queue()
constants.REPEATS = 3

constants.JOB_LIKELIHOOD = 1e-3
constants.FPGA_IDLE_SLEEP = 5e-1

exp = SimpleSimulation()
exp.simulateEpisode()