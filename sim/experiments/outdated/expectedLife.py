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

jump = 1
totalTime = 1e2
def runThread(likelihood, alpha, results, finished):
	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	sim.simulations.constants.EXPECTED_LIFETIME_ALPHA = alpha
	sim.simulations.constants.JOB_LIKELIHOOD = likelihood
	exp = simulation(hardwareAccelerated=True)
	sim.simulations.current = exp
	# exp.simulateTime(30)

	counter = 0

	for i in range(int(totalTime/jump)):
		exp.simulateTime(jump)
		counter += 1
		# print("counter", counter)
		results.put(["Lifetime Alpha = {:.4f} Likelihood = {:.4f}".format(alpha, likelihood), i * jump, exp.devicesLifetimes()])
		results.put(["Power Alpha = {:.4f} Likelihood = {:.4f}".format(alpha, likelihood), i * jump, [dev.averagePower for dev in exp.devices]])
		# print("\ntime", exp.time, "lifetime", exp.systemLifetime())
		# print("life ", [dev.expectedLifetime() for dev in exp.devices])
		# print("power", [dev.averagePower for dev in exp.devices])


	
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.simulations.constants.SAMPLE_SIZE = sim.simulations.variable.Gaussian(10, 2)
	sim.simulations.constants.SAMPLE_RAW_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.SAMPLE_PROCESSED_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.simulations.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
	sim.simulations.constants.MINIMUM_BATCH = 10
	sim.simulations.constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e2
	sim.simulations.constants.NUM_DEVICES = 1

	processes = list()
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.simulations.constants.REPEATS = 1

	alpha = 1e-4
	for alpha in np.logspace(-4, -3, num=3, endpoint=True):
	# if True:
		for likelihood in np.linspace(1e-3, 9e-3, num=1, endpoint=True):
			for _ in range(sim.simulations.constants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(likelihood, alpha, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished, numResults=2*int(totalTime/jump * len(processes)))
	print('plot time')
	sim.plotting.plotMultiWithErrors("expectedLife", results=results, separate=False) # , save=True)

if __name__ == "__main__":
	try:
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print ("ERROR")