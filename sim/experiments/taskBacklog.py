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
jump = 10
def runThread(jobLikelihood, totalTime, results):
	sim.constants.JOB_LIKELIHOOD = jobLikelihood

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = simulation(0, numDevices, 0, hardwareAccelerated=True)
	for i in range(int(totalTime/jump)):
		exp.simulateTime(jump)
		results.put(["Job Likelihood: {:.4f}".format(jobLikelihood), i, np.max(exp.taskQueueLength)])
		print(jobLikelihood, i)

	print(jobLikelihood, "done")


def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.ANYTHING
	sim.constants.MINIMUM_BATCH = 10
	sim.constants.MAXIMUM_TASK_QUEUE = 1e5

	processes = list()
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	sim.constants.REPEATS = 1
	totalTime = 500

	for jobLikelihood in np.arange(1e-3, 10e-3, 1e-3):
		# for totalTime in range(10):
		# for fpgaPowerPlan in [sim.fpgaPowerPolicy.FPGA_STAYS_ON]: # , sim.constants.FPGA_IMMEDIATELY_OFF, sim.constants.FPGA_WAIT_OFF]:
		for i in range(sim.constants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, totalTime, results)))
	
	print("executing...")
	experiment.executeMulti(processes)
	print("done executing...")
	# for process in processes: process.join()

	sim.plotting.plotMultiWithErrors("backlog", results=experiment.assembleResults(results, numResults=totalTime/jump * len(processes))) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")