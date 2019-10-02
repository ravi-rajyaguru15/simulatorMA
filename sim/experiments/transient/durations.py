import sim.constants
import sim.variable
import sim.debug
from sim.simulation import simulation
import sim.plotting
import sim.experiments.experiment
import sim.offloadingDecision
import sim.job

import numpy as np
import multiprocessing
import sys
import traceback
import warnings
import profile

sim.constants.NUM_DEVICES = 1

def runThread(numJobs, results, finished, histories):
	exp = simulation(hardwareAccelerated=True)
	sim.simulation.current = exp

	try:
		for e in range(numJobs):
			exp.simulateUntilJobDone()
			results.put(["Job Duration", e, sim.job.job.jobResultsQueue.get()])
	except:
		traceback.print_exc(file=sys.stdout)
		sys.exit(0)
		print("Error in experiment:", exp.time)

	finished.put(True)
	histories.put(sim.results.learningHistory)

	print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.DRAW = False
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
	# sim.constants.TOTAL_TIME = 1e3
	sim.constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e-1

	processes = list()
	sim.constants.MINIMUM_BATCH = 1
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	histories = multiprocessing.Queue()
	sim.constants.REPEATS = 1

	# for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
	# 	for roundRobin in np.arange(1e0, 1e1, 2.5):
	numJobs = 50
	for _ in range(sim.constants.REPEATS):
		processes.append(multiprocessing.Process(target=runThread, args=(numJobs, results, finished, histories)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished, numResults=numJobs*sim.constants.REPEATS)
	
	sim.plotting.plotMultiWithErrors("Episode duration", results=results, ylabel="Loss", xlabel="Job #") # , save=True)
	sim.plotting.plotAgentHistory(histories.get())

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")