import sim.simulations.constants
import sim.simulations.variable
import sim.debug
from sim.simulation import simulation
import sim.plotting
import sim.experiments.experiment

import numpy as np
import multiprocessing
import sys
import traceback

numDevices = 4
def runThread(jobLikelihood, results, finished):
	sim.simulations.constants.JOB_LIKELIHOOD = jobLikelihood

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = simulation(0, numDevices, 0, hardwareAccelerated=True)

	try:
		exp.simulateTime(10)
	except:
		traceback.print_exc(file=sys.stdout)
		print("Error in experiment:", jobLikelihood, exp.time)

	results.put(["", jobLikelihood, np.average([dev.numJobs for dev in exp.devices]) / exp.time])
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.simulations.constants.DRAW = False
	sim.simulations.constants.SAMPLE_SIZE = sim.simulations.variable.Gaussian(10, 2)
	sim.simulations.constants.SAMPLE_RAW_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.SAMPLE_PROCESSED_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.simulations.constants.FPGA_IDLE_SLEEP = 0.5
	sim.simulations.constants.OFFLOADING_POLICY = sim.offloadingPolicy.ANYTHING

	processes = list()
	sim.simulations.constants.MINIMUM_BATCH = 5
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.simulations.constants.REPEATS = 6

	for jobLikelihood in np.arange(1e-4, 5e-3, 2e-4):
		for _ in range(sim.simulations.constants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished)

	sim.plotting.plotMultiWithErrors("Job Rate", results=results, ylabel="Job Rate (jobs/s)", xlabel="Job Likelihood") # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")