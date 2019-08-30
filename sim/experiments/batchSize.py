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

def totalEnergyBatchSizeThread(name, hw, offloadingPolicy, batchSize, results, finished):
	sim.constants.MINIMUM_BATCH = batchSize
	sim.constants.OFFLOADING_POLICY = offloadingPolicy # sim.constants.PEER_ONLY if offloading else sim.constants.LOCAL_ONLY

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = simulation(0, 4, 0, hardwareAccelerated=hw)

	# exp.simulateTime(0.1)
	# exp.devices[0].createNewJob(exp.time, hardwareAccelerated=hw)
	exp.simulateTime(10)

	if not exp.allDone():
		warnings.warn("not all devices done: {}".format(batchSize))

	results.put([name, batchSize, np.sum(exp.totalDevicesEnergy())])

	finished.put(True)


def totalEnergyBatchSize():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	processes = list()
	sim.constants.JOB_LIKELIHOOD = 2e-3
		
	hwOptions = [True, False]
	offloadingOptions = sim.offloadingPolicy.OPTIONS
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.constants.REPEATS = 16

	for hw in hwOptions:
		for offloading in offloadingOptions:
			for batchSize in range(5, 30, 5):
				for i in range(sim.constants.REPEATS):				
					processes.append(multiprocessing.Process(target=totalEnergyBatchSizeThread, args=("HW Accelerator {} Offloading {}".format(hw, offloading), hw, offloading, batchSize, results, finished)))
	
	results = experiment.executeMulti(processes, results, finished)
	
	sim.plotting.plotMultiWithErrors("totalEnergyBatchSize", results=results) # , save=True)

try:
	totalEnergyBatchSize()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")