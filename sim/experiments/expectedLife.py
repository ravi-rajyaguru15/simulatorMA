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

numDevices = 1
jump = 1
totalTime = 1e3
def runThread(alpha, results, finished):
	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	sim.constants.EXPECTED_LIFETIME_ALPHA = alpha
	exp = simulation(0, numDevices, 0, hardwareAccelerated=True)
	for i in range(int(totalTime/jump)):
		exp.simulateTime(jump)
		results.put(["Alpha = {:.4f}".format(alpha), i * jump, exp.devicesLifetimes()])
	
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.ANYTHING
	sim.constants.JOB_LIKELIHOOD = 5e-3
	sim.constants.MINIMUM_BATCH = 10
	sim.constants.THREAD_COUNT = 1e3

	processes = list()
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.constants.REPEATS = 1

	for alpha in np.linspace(-6, -3, num=4, endpoint=True):
		for _ in range(sim.constants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(alpha, results, finished)))
	
	results = experiment.executeMulti(processes, results, finished, numResults=int(totalTime/jump * len(processes)))
	print ('plot time')
	sim.plotting.plotMultiWithErrors("expectedLife", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")