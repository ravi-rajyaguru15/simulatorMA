
import multiprocessing

import sys
import traceback


from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti
from sim.experiments.scenario import REGULAR_SCENARIO_ROUND_ROBIN
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.minimalDeepAgent import minimalDeepAgent
from sim.learning.agent.randomAgent import randomAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.learning.state.basicSystemState import basicSystemState
from sim.learning.state.extendedSystemState import extendedSystemState
from sim.simulations import localConstants, constants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.experiments.experiment import assembleResultsBasic, assembleResults

from sim.tasks.tasks import HARD
maxjobs = 5
numEnergyStates = 3


def runThread(id, agent, systemState, productionMode, offPolicy, numPhases, numEpisodes, results, finished):
	exp = SimpleSimulation(numDevices=4, maxJobs=maxjobs, agentClass=agent, tasks=[HARD], systemStateClass=systemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=True, numEnergyLevels=numEnergyStates, trainClassification=True, offPolicy=offPolicy, allowExpansion=True)

	exp.setBatterySize(1e-1)
	exp.setFpgaIdleSleep(1e-3)
	exp.sharedAgent.loadModel()
	exp.sharedAgent.setProductionMode(productionMode)

	e = None
	overallEpisode = 0
	try:
		for phase in range(numPhases):
			for e in range(numEpisodes):
				debug.infoEnabled = False
				exp.simulateEpisode(e)

				agentName = exp.devices[0].agent.__name__
				result = [f"{agentName} Production: {productionMode} OffPolicy: {offPolicy}", overallEpisode + e, exp.numFinishedJobs]
				# print("result", result)
				results.put(result)
				# results.put([f"{agentName}", e, exp.getCurrentTime()])

			# check if not the last one
			if phase < numPhases - 1:
				beforeStates = exp.currentSystemState.getUniqueStates()
				for i in range(5):
					exp.expandState("jobsInQueue")

				# print("\nexpand:", beforeStates, exp.currentSystemState.getUniqueStates())
				# print()
			overallEpisode += numEpisodes
	except:
		debug.printCache( )
		traceback.print_exc(file=sys.stdout)
		print(agent, e, offPolicy, productionMode)
		print("Error in experiment :", exp.time)
		sys.exit(0)

	finished.put(True)


def run(numEpisodes):
	print("starting experiment")

	processes = list()
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()

	localConstants.REPEATS = 8
	numEpisodes = int(numEpisodes)
	# , ]minimalTableAgent
	systemState = extendedSystemState

	numPhases = int(1e1)
	for agent, offPolicy, production in [(minimalDeepAgent, True, False), (minimalDeepAgent, False, False), (minimalDeepAgent, False, True), (minimalTableAgent, True, False),(minimalTableAgent, False, False), (minimalTableAgent, False, False)]: 
		for _ in range(localConstants.REPEATS):
			for centralised in [True]:
				# if not (not centralised and agent is randomAgent):
				processes.append(multiprocessing.Process(target=runThread, args=(
					len(processes), agent, systemState, production, offPolicy, numPhases, numEpisodes, results, finished)))

	results = executeMulti(processes, results, finished, numResults=len(
		processes) * numPhases * numEpisodes, assembly=assembleResults, chooseBest=1.0)

	# plotting.plotMultiWithErrors("experiment1", title="experiment 1", results=results, ylabel="", xlabel="Episode #")  # , save=True)
	plotting.plotMultiWithErrors("experiment5", title="experiment 5", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)


if __name__ == "__main__":
	setupMultithreading()
	try:
		run(1e1)
	except:
		traceback.print_exc(file=sys.stdout)

		print("ERROR")
