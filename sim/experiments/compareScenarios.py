import multiprocessing

import sys
import traceback
from multiprocessing import freeze_support

from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti
from sim.experiments.scenario import ALL_SCENARIOS, RANDOM_SCENARIO_RANDOM
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation


def runThread(scenario, numEpisodes, results, finished):
	exp = SimpleSimulation(maxJobs=6, scenarioTemplate=scenario)
	exp.setBatterySize(1e0)
	e = -1

	try:
		for e in range(numEpisodes):
			exp.simulateEpisode()

			results.put([str(scenario), e, exp.numFinishedJobs])
	except:
		debug.printCache()
		traceback.print_exc(file=sys.stdout)
		print(scenario, e)
		print("Error in experiment ̰:", exp.time)
		sys.exit(0)

	try:
		finished.put(True)
	except:
		traceback.print_stack()
	print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)

	# exp.sharedAgent.printModel()


def run(numEpisodes):
	multiprocessing.set_start_method('spawn')
	print("starting experiment")
	debug.enabled = False
	debug.learnEnabled = False
	debug.infoEnabled = False
	debug.settings.fileOutput = False
	localConstants.DEBUG_HISTORY = False
	debug.settings.maxCache = int(1e4)

	processes = list()

	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()

	numEpisodes = int(numEpisodes)
	print(ALL_SCENARIOS, localConstants.REPEATS)
	for scenario in ALL_SCENARIOS:
		for _ in range(localConstants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(scenario, numEpisodes, results, finished)))

	results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodes)

	plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)


if __name__ == "__main__":
	freeze_support()
	try:
		run(1e2)
	except:
		traceback.print_exc(file=sys.stdout)

		print("ERROR")