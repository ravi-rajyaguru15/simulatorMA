import sim.constants
import sim.variable
import sim.debug
from sim.sim import simulation
import sim.plotting
import experiment

import numpy as np
import multiprocessing

def totalEnergyJobSizeThread(name, hw, samples, results):
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)

	exp = simulation(0, 1, 0, visualise=False)

	exp.simulateTime(0.1)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=hw)
	exp.simulateTime(10)
	if not exp.allDone():
		raise Exception("not all devices done: {}".format(samples))

	results.put([name, samples, np.sum(exp.totalDevicesEnergy())])


def totalEnergyJobSize():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = sim.constants.LOCAL_ONLY
	sim.constants.MINIMUM_BATCH = 1
	sim.constants.JOB_LIKELIHOOD = 0
	
	processes = list()
	hwOptions = [True, False]
	results = multiprocessing.Queue()
	samplesList = range(1, 1000, 10)

	for hw in hwOptions:
		for samples in samplesList:
			for i in range(sim.constants.REPEATS):				
				processes.append(multiprocessing.Process(target=totalEnergyJobSizeThread, args=("HW Acceleration {}".format(hw), hw, samples, results)))
	
	for process in processes: process.start()
	# for process in processes: process.join()

	sim.plotting.plotMultiWithErrors("totalEnergyJobSize", results=experiment.assembleResults(len(processes), results), save=True)

try:
	totalEnergyJobSize()
except:
	print ("ERROR")