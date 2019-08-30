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

numDevices = 4
def runThread(jobLikelihood, offloadingPolicy, results, finished):
	sim.constants.OFFLOADING_POLICY = offloadingPolicy
	sim.constants.JOB_LIKELIHOOD = jobLikelihood

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = simulation(0, numDevices, 0, hardwareAccelerated=True)

	exp.simulateTime(10)

	# if not exp.allDone():
	# 	warnings.warn("not all devices done: {}".format(numDevices))

	results.put(["{}".format(offloadingPolicy), jobLikelihood, np.average([dev.totalSleepTime for dev in exp.devices])])
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF

	processes = list()
	sim.constants.MINIMUM_BATCH = 5
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.constants.REPEATS = 6

	for jobLikelihood in np.arange(1e-2, 10e-2, 1e-2):
		# for fpgaPowerPlan in [sim.fpgaPowerPolicy.FPGA_STAYS_ON]: # , sim.constants.FPGA_IMMEDIATELY_OFF, sim.constants.FPGA_WAIT_OFF]:
		for offloading in sim.offloadingPolicy.OPTIONS:
			for i in range(sim.constants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, offloading, results, finished)))
	
	results = experiment.executeMulti(processes, results, finished)
	sim.plotting.plotMultiWithErrors("sleep time", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")