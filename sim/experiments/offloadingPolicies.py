import sim.constants
import sim.variable
import sim.debug
from sim.simulation import simulation
import sim.plotting
import sim.offloadingPolicy
import experiment

import numpy as np
import multiprocessing
import sys
import traceback
import warnings

numDevices = 4
def runThread(name, jobLikelihood, offloadingPolicy, results):
	sim.constants.OFFLOADING_POLICY = offloadingPolicy
	sim.constants.JOB_LIKELIHOOD = jobLikelihood

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = simulation(0, numDevices, 0, visualise=False, hardwareAccelerated=True)

	# exp.simulateTime(0.1)
	# exp.devices[0].createNewJob(exp.time, hardwareAccelerated=hw)
	exp.simulateTime(10)

	if not exp.allDone():
		warnings.warn("not all devices done: {}".format(numDevices))

	results.put([name, jobLikelihood, np.sum(exp.totalDevicesEnergy()) / numDevices])


def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)

	processes = list()
	sim.constants.MINIMUM_BATCH = 5
	
	offloadingOptions = [sim.offloadingPolicy.LOCAL_ONLY, sim.offloadingPolicy.RANDOM_PEER_ONLY, sim.offloadingPolicy.SPECIFIC_PEER_ONLY, sim.offloadingPolicy.ANYTHING]
	results = multiprocessing.Queue()
	sim.constants.REPEATS = 6

	for jobLikelihood in np.arange(1e-2, 10e-2, 1e-2):
		for offloadingPolicy in offloadingOptions:
			for i in range(sim.constants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=("Offloading {}".format(offloadingPolicy), jobLikelihood, offloadingPolicy, results)))
	
	for process in processes: process.start()
	# for process in processes: process.join()

	sim.plotting.plotMultiWithErrors("offloadingPolicy", results=experiment.assembleResults(len(processes), results)) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")