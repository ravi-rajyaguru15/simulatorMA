import sim.constants
import sim.variable
import sim.debug
from sim.simulation import simulation
import sim.plotting
import sim.offloadingPolicy
import sim.experiments.experiment

import numpy as np
import multiprocessing
import sys
import traceback
import warnings

numDevices = 4
def runThread(jobLikelihood, offloadingPolicy, results, finished):
	sim.constants.OFFLOADING_POLICY = offloadingPolicy
	sim.constants.JOB_LIKELIHOOD = jobLikelihood

	exp = simulation(0, numDevices, 0, hardwareAccelerated=True)

	exp.simulateTime(10)

	# if not exp.allDone():
	# 	warnings.warn("not all devices done: {}".format(numDevices))

	results.put(["Offloading {}".format(offloadingPolicy), jobLikelihood, np.sum(exp.totalDevicesEnergy()) / numDevices])
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.FPGA_IDLE_SLEEP = 0.25

	processes = list()
	sim.constants.MINIMUM_BATCH = 5
	
	offloadingOptions = sim.offloadingPolicy.OPTIONS
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	
	sim.constants.REPEATS = 3

	for jobLikelihood in np.arange(1e-3, 10e-3, 1e-3):
		for offloadingPolicy in offloadingOptions:
			for i in range(sim.constants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, offloadingPolicy, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished)

	sim.plotting.plotMultiWithErrors("offloadingPolicy", results=results) # , save=True)

	# for process in processes: process.join()


try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")