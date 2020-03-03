import multiprocessing
import sys
import traceback
from multiprocessing import freeze_support

import sim.debug as debug
import sim.simulations.constants as constants
from sim import plotting
from sim.experiments.experiment import executeMulti
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.localAgent import localAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.randomAgent import randomAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.offloading.offloadingPolicy import *
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation, SimpleSimulation


def runThread(agent, numEpisodes, results, finished, histories):
	exp = SimpleSimulation(numDevices=2, maxJobs=6, agentClass=agent)

	try:
		for e in range(int(numEpisodes/2)):
			exp.simulateEpisode()

			results.put(["Agent %s" % agent.__name__, e, exp.numFinishedJobs])

		exp.sharedAgent.setProductionMode(True)
		for e in range(int(numEpisodes/2), int(numEpisodes)):
			exp.simulateEpisode()

			results.put(["Agent %s" % agent.__name__, e, exp.numFinishedJobs])
	except:
		debug.printCache(200)
		traceback.print_exc(file=sys.stdout)
		print(agent)
		print("Error in experiment ̰:", exp.time)
		sys.exit(0)

	finished.put(True)

	exp.sharedAgent.printModel()


def run():
	print("starting experiment")
	debug.enabled = False
	debug.learnEnabled = False
	debug.infoEnabled = False


	processes = list()
	# sim.simulations.constants.MINIMUM_BATCH = 1e7

	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	histories = multiprocessing.Queue()
	# REPEATS = 1

	# localConstants.REPEATS = 10
	numEpisodes = int(1e2)
	agentsToTest = [minimalAgent, lazyAgent]
	for agent in agentsToTest: # [minimalAgent, lazyAgent]:
		for _ in range(localConstants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished, histories)))

	results = executeMulti(processes, results, finished, numResults=len(agentsToTest) * numEpisodes * localConstants.REPEATS)

	plotting.plotMultiWithErrors("Number of Jobs (with production mode)", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)


if __name__ == "__main__":
	freeze_support()
	try:
		run()
	except:
		traceback.print_exc(file=sys.stdout)
		print("ERROR")

