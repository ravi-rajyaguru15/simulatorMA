import sim.constants
import sim.variable
import sim.debug
from sim.simulation import simulation
import sim.plotting
import sim.experiments.experiment

import numpy as np
import multiprocessing
import sys
import traceback
import warnings

jump = 1
totalTime = 1e2
def runThread(alpha, results, finished):
	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	sim.constants.EXPECTED_LIFETIME_ALPHA = alpha
	exp = simulation(hardwareAccelerated=True)
	sim.simulation.current = exp
	counter = 0
	for i in range(int(totalTime/jump)):
		exp.simulateTime(jump)
		counter += 1
		print("counter", counter)
		results.put(["Lifetime Alpha = {:.4f}".format(alpha), i * jump, exp.devicesLifetimes()])
		results.put(["Power Alpha = {:.4f}".format(alpha), i * jump, [dev.averagePower for dev in exp.devices]])
		# print("\ntime", exp.time, "lifetime", exp.systemLifetime())
		# print("life ", [dev.expectedLifetime() for dev in exp.devices])
		# print("power", [dev.averagePower for dev in exp.devices])
	
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
	sim.constants.JOB_LIKELIHOOD = 1e-2
	sim.constants.MINIMUM_BATCH = 10
	sim.constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e2
	sim.constants.NUM_DEVICES = 2

	processes = list()
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.constants.REPEATS = 1

	alpha = 1e-4
	# for alpha in np.logspace(-4, -3, num=2, endpoint=True):
	if True:
		for _ in range(sim.constants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(alpha, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished, numResults=2*int(totalTime/jump * len(processes)))
	print ('plot time')
	sim.plotting.plotMultiWithErrors("expectedLife", results=results, separate=True) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")