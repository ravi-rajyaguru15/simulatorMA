import sim.constants
import sim.variable
import sim.debug
from sim.simulation import simulation
import sim.plotting
import sim.experiments.experiment
import sim.offloadingDecision

import numpy as np
import multiprocessing
import sys
import traceback
import warnings
import profile

sim.constants.NUM_DEVICES = 4
numJobs = int(1e2)
def runThread(results, finished):
	exp = simulation(hardwareAccelerated=True)

	try:
		for i in range(numJobs):
			exp.simulateUntilJobDone()
			results.put(["Loss", exp.completedJobs, sim.offloadingDecision.offloadingDecision.learningAgent.loss])
			results.put(["Reward", exp.completedJobs, sim.offloadingDecision.offloadingDecision.learningAgent.latestReward])
			results.put(["Action", exp.completedJobs, sim.offloadingDecision.offloadingDecision.learningAgent.latestAction])
	except:
		traceback.print_exc(file=sys.stdout)
		sys.exit(0)
		print("Error in experiment:", exp.time)

	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.DRAW = False
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
	# sim.constants.TOTAL_TIME = 1e3

	processes = list()
	sim.constants.MINIMUM_BATCH = 5
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.constants.REPEATS = 100

	# for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
	# 	for roundRobin in np.arange(1e0, 1e1, 2.5):
	for _ in range(sim.constants.REPEATS):
		processes.append(multiprocessing.Process(target=runThread, args=(results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished, numResults=numJobs*sim.constants.REPEATS*3)
	
	sim.plotting.plotMultiWithErrors("Learning Loss", results=results, ylabel="Loss", xlabel="Job #") # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")