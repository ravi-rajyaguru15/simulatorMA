import multiprocessing
import sys
import traceback

from sim import debug, counters
from sim.devices.components.powerPolicy import IDLE_TIMEOUT
from sim.experiments.experiment import executeMulti
from sim.learning.agent.minimalAgent import minimalAgent
from sim.offloading.offloadingPolicy import REINFORCEMENT_LEARNING
from sim.plotting import plotAgentHistory, plotMultiWithErrors
from sim.simulations import constants, simulationResults
from sim.simulations.SimpleSimulation import SimpleSimulation as simulation
from sim.tasks.job import job

constants.NUM_DEVICES = 1
numJobs = int(1e3)


def runThread(results, finished, histories):
	print("creating simulation", constants.OFFLOADING_POLICY)
	debug.enabled = False
	constants.DRAW = False
	constants.FPGA_POWER_PLAN = IDLE_TIMEOUT
	constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING

	exp = simulation(agentClass=minimalAgent)
	current = exp

	try:
		for i in range(numJobs):
			exp.simulateUntilJobDone()
			batch = job.jobResultsQueue.get()
			batch = batch[0]
			# print("batch:", batch)
			results.put(["Batch Size", exp.completedJobs, batch])
	except:
		print("Error in experiment:", exp.time)
		traceback.print_exc(file=sys.stdout)
		debug.printCache()
		sys.exit(0)

	finished.put(True)
	histories.put(simulationResults.learningHistory)

	print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)
	exp.sharedAgent.printModel()


def run():
	print ("starting experiment")

	# sim.constants.TOTAL_TIME = 1e3

	processes = list()
	constants.MINIMUM_BATCH = 1e5
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	histories = multiprocessing.Queue()
	constants.REPEATS = 1
	constants.MAX_JOBS = 5

	# for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
	# 	for roundRobin in np.arange(1e0, 1e1, 2.5):
	for _ in range(constants.REPEATS):
		processes.append(multiprocessing.Process(target=runThread, args=(results, finished, histories)))
	
	results = executeMulti(processes, results, finished, numResults=numJobs * constants.REPEATS)

	plotMultiWithErrors("BatchSize", results=results, ylabel="Loss", xlabel="Job #") # , save=True)
	# plotAgentHistory(histories.get())


if __name__ == "__main__":
	try:
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print ("ERROR")