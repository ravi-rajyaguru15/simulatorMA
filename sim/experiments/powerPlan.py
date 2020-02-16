import multiprocessing
import sys
import traceback

import numpy as np
from sim.simulation import simulation

import sim.debug
import sim.experiments.experiment
import sim.plotting
import sim.simulations.constants
import sim.simulations.variable

numDevices = 4
def runThread(jobLikelihood, offloadingPolicy, fpgaPowerPlan, results, finished):
	sim.simulations.constants.OFFLOADING_POLICY = offloadingPolicy
	sim.simulations.constants.FPGA_POWER_PLAN = fpgaPowerPlan
	sim.simulations.constants.JOB_LIKELIHOOD = jobLikelihood

	exp = simulation(0, numDevices, 0, hardwareAccelerated=True)

	exp.simulateTime(10)

	# if not exp.allDone():
	# 	warnings.warn("not all devices done: {}".format(numDevices))

	results.put(["{} FPGA {}".format(offloadingPolicy, fpgaPowerPlan), jobLikelihood, np.sum(exp.totalDevicesEnergy()) / numDevices])
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.simulations.constants.SAMPLE_SIZE = sim.simulations.variable.Gaussian(10, 2)
	sim.simulations.constants.SAMPLE_RAW_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.SAMPLE_PROCESSED_SIZE = sim.simulations.variable.Constant(4, integer=True)

	processes = list()
	sim.simulations.constants.JOB_LIKELIHOOD = 2e-3
	sim.simulations.constants.MINIMUM_BATCH = 5
	
	offloadingOptions = sim.offloadingPolicy.OPTIONS
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.simulations.constants.REPEATS = 6

	for jobLikelihood in np.arange(1e-2, 10e-2, 1e-2):
		for fpgaPowerPlan in sim.powerPolicy.OPTIONS: # , sim.constants.FPGA_IMMEDIATELY_OFF, sim.constants.FPGA_WAIT_OFF]:
			for offloading in offloadingOptions:
					for i in range(sim.simulations.constants.REPEATS):
						processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, offloading, fpgaPowerPlan, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished)
	# for process in processes: process.join()

	sim.plotting.plotMultiWithErrors("fpgaPowerPlan", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")