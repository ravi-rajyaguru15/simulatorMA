import multiprocessing
import sys
import traceback

import numpy as np

from sim.experiments.experiment import executeMulti
from sim.plotting import plotMultiWithErrors
from sim.simulations.SimpleSimulation import SimpleSimulation

numDevices = 4
def runThread(exp, jobInterval, results, finished):
	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)

	# exp.simulateTime(10)
	exp.simulateEpisode()


	results.put(["", jobInterval, np.average([dev.totalSleepTime for dev in exp.devices])])
	finished.put(True)

def run():
	print ("starting experiment")

	processes = list()

	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	REPEATS = 6

	for jobInterval in np.arange(1e1, 1e2, 1e1):
		# for fpgaPowerPlan in [sim.fpgaPowerPolicy.FPGA_STAYS_ON]: # , sim.constants.FPGA_IMMEDIATELY_OFF, sim.constants.FPGA_WAIT_OFF]:
		for _ in range(REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(SimpleSimulation(maxJobs=5, numDevices=numDevices, jobInterval=jobInterval), jobInterval, results, finished)))
	
	results = executeMulti(processes, results, finished)
	plotMultiWithErrors("sleep time", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")