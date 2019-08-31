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
def runThread(offloading, jobLikelihood, numTicks , results, finished):
	sim.constants.JOB_LIKELIHOOD = jobLikelihood

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = simulation(0, numDevices, 0, hardwareAccelerated=True)

	for i in range(numTicks):
		exp.simulateTick()
	results.put(["Offloading Policy {}".format(offloading), jobLikelihood, np.average(exp.delays)])
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY
	sim.constants.DRAW = False

	processes = list()
	# sim.constants.MINIMUM_BATCH = 5
	
	numTicks = 10000

	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.constants.REPEATS = 9

	for jobLikelihood in np.arange(1e-3, 2e-2, 1e-3):
		# for fpgaPowerPlan in [sim.fpgaPowerPolicy.FPGA_STAYS_ON]: # , sim.constants.FPGA_IMMEDIATELY_OFF, sim.constants.FPGA_WAIT_OFF]:
		for offloading in sim.offloadingPolicy.OPTIONS:
			for i in range(sim.constants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(offloading, jobLikelihood, numTicks, results, finished)))
	
	results = experiment.executeMulti(processes, results, finished)
	sim.plotting.plotMultiWithErrors("delays", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")