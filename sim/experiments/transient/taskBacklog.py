import sim.simulations.constants
import sim.simulations.variable
import sim.debug
from sim.simulation import simulation
import sim.plotting
import sim.experiments.experiment

import numpy as np
import multiprocessing
import sys
import traceback

numDevices = 4
jump = 10
def runThread(jobLikelihood, totalTime, results, finished):
	sim.simulations.constants.JOB_LIKELIHOOD = jobLikelihood

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = simulation(0, numDevices, 0, hardwareAccelerated=True)
	for i in range(int(totalTime/jump)):
		exp.simulateTime(jump)
		results.put(["Job Likelihood: {:.4f}".format(jobLikelihood), i * jump, np.max(exp.taskQueueLength)])
	
	finished.put(True)
		# print(jobLikelihood, i)

	# print(jobLikelihood, "done")


def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.simulations.constants.SAMPLE_SIZE = sim.simulations.variable.Gaussian(10, 2)
	sim.simulations.constants.SAMPLE_RAW_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.SAMPLE_PROCESSED_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF
	sim.simulations.constants.OFFLOADING_POLICY = sim.offloadingPolicy.ANYTHING
	sim.simulations.constants.MINIMUM_BATCH = 10
	sim.simulations.constants.MAXIMUM_TASK_QUEUE = 1e5
	sim.simulations.constants.THREAD_COUNT = 1e3

	processes = list()
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.simulations.constants.REPEATS = 1
	totalTime = 500

	for jobLikelihood in np.arange(1e-3, 10e-3, 1e-3):
		# for totalTime in range(10):
		# for fpgaPowerPlan in [sim.fpgaPowerPolicy.FPGA_STAYS_ON]: # , sim.constants.FPGA_IMMEDIATELY_OFF, sim.constants.FPGA_WAIT_OFF]:
		for i in range(sim.simulations.constants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, totalTime, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished, numResults=int(totalTime/jump * len(processes)))

	sim.plotting.plotMultiWithErrors("backlog", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")