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
def runThread(jobLikelihood, roundRobin, results, finished):
	sim.simulations.constants.ROUND_ROBIN_TIMEOUT = roundRobin
	sim.simulations.constants.JOB_LIKELIHOOD = jobLikelihood

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = simulation(0, numDevices, 0, hardwareAccelerated=True)

	try:
		exp.simulateTime(sim.simulations.constants.TOTAL_TIME)
	except:
		traceback.print_exc(file=sys.stdout)
		print("Error in experiment:", jobLikelihood, roundRobin, exp.time)

	results.put(["Round Robin {}".format(roundRobin), jobLikelihood, np.sum(exp.totalDevicesEnergy()) / numDevices])
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.simulations.constants.DRAW = False
	sim.simulations.constants.SAMPLE_SIZE = sim.simulations.variable.Gaussian(10, 2)
	sim.simulations.constants.SAMPLE_RAW_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.SAMPLE_PROCESSED_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.simulations.constants.OFFLOADING_POLICY = sim.offloadingPolicy.ROUND_ROBIN
	sim.simulations.constants.TOTAL_TIME = 1e3

	processes = list()
	sim.simulations.constants.MINIMUM_BATCH = 5
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.simulations.constants.REPEATS = 3

	for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
		for roundRobin in np.arange(1e0, 1e1, 2.5):
			for _ in range(sim.simulations.constants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, roundRobin, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished)
	
	sim.plotting.plotMultiWithErrors("Average Energy", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")