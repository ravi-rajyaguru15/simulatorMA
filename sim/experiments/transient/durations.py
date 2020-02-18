import multiprocessing
import sys
import traceback

from sim.simulation import simulation

import sim.debug
import sim.experiments.experiment
import sim.plotting
import sim.simulations.constants
import sim.simulations.variable
import sim.tasks.job

sim.simulations.constants.NUM_DEVICES = 1

def runThread(numJobs, results, finished, histories):
	exp = simulation(hardwareAccelerated=True)
	sim.simulations.current = exp

	try:
		for e in range(numJobs):
			exp.simulateUntilJobDone()
			results.put(["Job Duration", e, sim.tasks.job.job.jobResultsQueue.get()])
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
	sim.simulations.constants.DRAW = False
	sim.simulations.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.simulations.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
	# sim.constants.TOTAL_TIME = 1e3
	sim.simulations.constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e-1

	processes = list()
	sim.simulations.constants.MINIMUM_BATCH = 1
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	histories = multiprocessing.Queue()
	sim.simulations.constants.REPEATS = 1

	# for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
	# 	for roundRobin in np.arange(1e0, 1e1, 2.5):
	numJobs = 50
	for _ in range(sim.simulations.constants.REPEATS):
		processes.append(multiprocessing.Process(target=runThread, args=(numJobs, results, finished, histories)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished, numResults=numJobs * sim.simulations.constants.REPEATS)
	
	sim.plotting.plotMultiWithErrors("Episode duration", results=results, ylabel="Loss", xlabel="Job #") # , save=True)
	sim.plotting.plotAgentHistory(histories.get())

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")