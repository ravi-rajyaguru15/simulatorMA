
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
from sim.learning.state.targetedSystemState import targetedSystemState
from sim.simulations import localConstants, constants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.experiments.experiment import assembleResultsBasic, assembleResults

from sim.tasks.tasks import *
maxjobs = 5
numEnergyStates = 3

def runThread(id, agent, systemState, offPolicy, tasks, numPhases, numEpisodes, results, finished):
	exp = SimpleSimulation(numDevices=4, maxJobs=maxjobs, agentClass=agent, tasks=tasks[:1], systemStateClass=systemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=False, numEnergyLevels=numEnergyStates, trainClassification=True, offPolicy=offPolicy, allowExpansion=False)

	exp.setBatterySize(1e-1)
	exp.setFpgaIdleSleep(1e-3)

	e = None
	overallEpisode = 0
	try:
		for phase in range(numPhases):
			for e in range(numEpisodes):
				debug.infoEnabled = False
				exp.simulateEpisode(e)

				agentName = exp.devices[0].agent.__name__
				result = [f"{agentName} OffPolicy: {offPolicy}", overallEpisode + e, exp.numFinishedJobs]
				# print("result", result)
				results.put(result)
				# results.put([f"{agentName}", e, exp.getCurrentTime()])

			# check if not the last one
			if phase < numPhases - 1:
				exp.tasks = tasks[:(phase + 2)]
				exp.expandState("taskId")


			overallEpisode += numEpisodes
	except:
		debug.printCache( )
		traceback.print_exc(file=sys.stdout)
		print(agent, e, offPolicy)
		print("Error in experiment :", exp.time)
		sys.exit(0)

	finished.put(True)


def run(numEpisodes):
	print("starting experiment")

	processes = list()
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()

	localConstants.REPEATS = 32
	numEpisodes = int(numEpisodes)
	# , ]minimalTableAgent
	systemState = targetedSystemState

	# tasks = [EASY, HARD, MEDIUM, ALTERNATIVE] # this works somewhat
	tasks = [EASY, MEDIUM, HARD, ALTERNATIVE][::-1] # comm is too hard?

	for t in range(len(tasks)):
		tasks[t].identifier = t
		print("task", tasks[t], tasks[t].identifier)

	numPhases = len(tasks)
	for agent, offPolicy in [(minimalDeepAgent, True), (minimalTableAgent, True)]: # (minimalDeepAgent, False),
		for _ in range(localConstants.REPEATS):
			for centralised in [True]:
				# if not (not centralised and agent is randomAgent):
				processes.append(multiprocessing.Process(target=runThread, args=(
					len(processes), agent, systemState, offPolicy, tasks, numPhases, numEpisodes, results, finished)))

	results = executeMulti(processes, results, finished, numResults=len(
		processes) * numPhases * numEpisodes, assembly=assembleResults, chooseBest=0.5)

	plotting.plotMultiWithErrors("experiment9", title="experiment 9", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)


if __name__ == "__main__":
	setupMultithreading()
	try:
		run(1e2)
	except:
		traceback.print_exc(file=sys.stdout)

		print("ERROR")
