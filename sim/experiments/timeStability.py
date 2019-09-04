import sim.constants
import sim.variable
import sim.debug
from sim.simulation import simulation
import sim.plotting
import experiment

import numpy as np
import multiprocessing
import sys
import traceback
import warnings
import profile

numDevices = 4
def runThread(jobLikelihood, totalTime, results, finished):
	sim.constants.JOB_LIKELIHOOD = jobLikelihood

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = simulation(0, numDevices, 0, hardwareAccelerated=True)

	try:
		exp.simulateTime(totalTime)
	except:
		traceback.print_exc(file=sys.stdout)
		print("Error in experiment:", jobLikelihood, totalTime, exp.time)

	results.put(["Total Time {}".format(totalTime), jobLikelihood, np.sum(exp.totalDevicesEnergy()) / numDevices])
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.DRAW = False
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.ROUND_ROBIN
	sim.constants.ROUND_ROBIN_TIMEOUT = 5


	processes = list()
	sim.constants.MINIMUM_BATCH = 5
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.constants.REPEATS = 3

	for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
		for totalTime in np.logspace(1, 3, 3, endpoint=True):
			for _ in range(sim.constants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, totalTime, results, finished)))
	
	results = experiment.executeMulti(processes, results, finished)
	
	sim.plotting.plotMultiWithErrors("Average Energy", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")