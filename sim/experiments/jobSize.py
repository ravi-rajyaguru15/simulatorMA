import sim.simulations.constants
import sim.simulations.variable
import sim.debug
import sim.simulation
import sim.plotting
import sim.experiments.experiment

import numpy as np
import multiprocessing

def totalEnergyJobSizeThread(hw, samples, results, finished):
	sim.simulations.constants.SAMPLE_SIZE = sim.simulations.variable.Constant(samples)

	exp = sim.simulations.simulation(0, 1, 0)

	exp.simulateTime(0.1)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=hw)
	exp.simulateTime(10)
	if not exp.allDone():
		raise Exception("not all devices done: {}".format(samples))

	results.put(["HW Acceleration {}".format(hw), samples, np.sum(exp.totalDevicesEnergy())])
	finished.put(True)

def totalEnergyJobSize():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.simulations.constants.OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
	sim.simulations.constants.MINIMUM_BATCH = 1
	sim.simulations.constants.JOB_LIKELIHOOD = 0
	
	processes = list()
	hwOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	samplesList = range(1, 1000, 10)

	for hw in hwOptions:
		for samples in samplesList:
			for i in range(sim.simulations.constants.REPEATS):
				processes.append(multiprocessing.Process(target=totalEnergyJobSizeThread, args=(hw, samples, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished)

	sim.plotting.plotMultiWithErrors("totalEnergyJobSize", results=results) #, save=True)

try:
	totalEnergyJobSize()
except:
	print ("ERROR")