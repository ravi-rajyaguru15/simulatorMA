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

def totalEnergyBatchSizeThread(name, hw, batchSize, results):
	sim.constants.MINIMUM_BATCH = batchSize

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = simulation(0, 1, 0, visualise=False, hardwareAccelerated=hw)

	# exp.simulateTime(0.1)
	# exp.devices[0].createNewJob(exp.time, hardwareAccelerated=hw)
	exp.simulateTime(10)

	if not exp.allDone():
		warnings.warn("not all devices done: {}".format(batchSize))

	results.put([name, batchSize, np.sum(exp.totalDevicesEnergy())])


def totalEnergyBatchSize():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = sim.constants.LOCAL_ONLY
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	processes = list()
	sim.constants.JOB_LIKELIHOOD = 2e-3
		
	hwOptions = [True, False]
	results = multiprocessing.Queue()
	sim.constants.REPEATS = 5

	for hw in hwOptions:
		for batchSize in range(1, 10):
			for i in range(sim.constants.REPEATS):				
				processes.append(multiprocessing.Process(target=totalEnergyBatchSizeThread, args=("HW Accelerator {}".format(hw), hw, batchSize, results)))
	
	for process in processes: process.start()
	# for process in processes: process.join()

	sim.plotting.plotMultiWithErrors("totalEnergyBatchSize", results=experiment.assembleResults(len(processes), results)) # , save=True)

try:
	totalEnergyBatchSize()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")