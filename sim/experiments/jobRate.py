import multiprocessing
import sys
import traceback

import numpy as np

import sim.debug
import sim.experiments.experiment
import sim.plotting
import sim.simulations.constants
import sim.simulations.variable
from sim import debug
from sim.devices.components import powerPolicy
from sim.offloading import offloadingPolicy
from sim.simulations import constants, variable
from sim.simulations.SimpleSimulation import SimpleSimulation

numDevices = 4
def runThread(jobLikelihood, results, finished):
	sim.simulations.constants.JOB_LIKELIHOOD = jobLikelihood

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = SimpleSimulation()

	try:
		exp.simulateTime(10)
	except:
		traceback.print_exc(file=sys.stdout)
		print("Error in experiment:", jobLikelihood, exp.time)

	results.put(["", jobLikelihood, np.average([dev.numJobs for dev in exp.devices]) / exp.time.current])
	finished.put(True)

def run():
	print("starting experiment")
	debug.enabled = False
	constants.DRAW = False
	constants.SAMPLE_SIZE = variable.Gaussian(10, 2)
	constants.SAMPLE_RAW_SIZE = variable.Constant(4, integer=True)
	constants.SAMPLE_PROCESSED_SIZE = variable.Constant(4, integer=True)
	constants.FPGA_POWER_PLAN = powerPolicy.IDLE_TIMEOUT
	constants.FPGA_IDLE_SLEEP = 0.5
	constants.OFFLOADING_POLICY = offloadingPolicy.ANYTHING

	processes = list()
	constants.MINIMUM_BATCH = 5
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	constants.REPEATS = 6

	for jobLikelihood in np.arange(1e-4, 5e-3, 2e-4):
		for _ in range(constants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished)

	sim.plotting.plotMultiWithErrors("Job Rate", results=results, ylabel="Job Rate (jobs/s)", xlabel="Job Likelihood") # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")