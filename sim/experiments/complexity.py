import sim.simulations.constants
import sim.simulations.variable
import sim.debug
from sim.simulation import simulation
import sim.plotting
import sim.offloading.offloadingPolicy
import sim.experiments.experiment

import numpy as np
import multiprocessing
import sys
import traceback

numDevices = 4
totalTime = 5e1
def runThread(jobLikelihood, offloadingPolicy, task, hw, results, finished):
	sim.simulations.constants.OFFLOADING_POLICY = offloadingPolicy
	sim.simulations.constants.JOB_LIKELIHOOD = jobLikelihood
	sim.simulations.constants.DEFAULT_TASK_GRAPH = [task]

	exp = simulation(0, numDevices, 0, hardwareAccelerated=hw)

	exp.simulateTime(totalTime)

	# if not exp.allDone():
	# 	warnings.warn("not all devices done: {}".format(numDevices))

	results.put(["{} - {} - HW {}".format(offloadingPolicy, task, hw), jobLikelihood, np.sum(exp.totalDevicesEnergy()) / numDevices])
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.simulations.constants.SAMPLE_SIZE = sim.simulations.variable.Gaussian(10, 2)
	sim.simulations.constants.SAMPLE_RAW_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.SAMPLE_PROCESSED_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.simulations.constants.FPGA_IDLE_SLEEP = 0.25

	processes = list()
	sim.simulations.constants.MINIMUM_BATCH = 5
	
	offloadingOptions = [sim.offloading.offloadingPolicy.ANYTHING, sim.offloading.offloadingPolicy.LOCAL_ONLY] # sim.offloadingPolicy.OPTIONS
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	
	sim.simulations.constants.REPEATS = 1

	for jobLikelihood in np.arange(1e-3, 10e-3, 2.5e-3):
		for offloadingPolicy in offloadingOptions:
			for task in [sim.tasks.EASY, sim.tasks.HARD]:
				for i in range(sim.simulations.constants.REPEATS):
					for hw in [True]: # , False]:
						processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, offloadingPolicy, task, hw, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished)

	sim.plotting.plotMultiWithErrors("Complexity", results=results) # , save=True)

	# for process in processes: process.join()


try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")