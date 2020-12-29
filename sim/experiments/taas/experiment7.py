
import multiprocessing

import sys
import traceback
from datetime import datetime

from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti
from sim.experiments.scenario import REGULAR_SCENARIO_ROUND_ROBIN
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.minimalDeepAgent import minimalDeepAgent
from sim.learning.agent.randomAgent import randomAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.learning.state.extendedSystemState import extendedSystemState
from sim.simulations import localConstants, constants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.experiments.experiment import assembleResultsBasic, assembleResults

from sim.tasks.tasks import HARD
maxjobs = 5
numEnergyStates = 3

def runThread(id, agent, pretrain, numEpisodes, results, finished):
	startTime = datetime.now()

	exp = SimpleSimulation(numDevices=4, maxJobs=maxjobs, agentClass=agent, tasks=[HARD], systemStateClass=extendedSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=True, numEnergyLevels=numEnergyStates, trainClassification=True, offPolicy=True)
	# exp.sharedAgent.precache = True
	# exp.scenario.setInterval(1)
	if pretrain:
		exp.sharedAgent.loadModel()
	exp.setBatterySize(1e-1)
	exp.setFpgaIdleSleep(1e-3)

	e = None
	try:
		for e in range(numEpisodes):
			debug.infoEnabled = False
			exp.simulateEpisode(e)

			agentName = exp.devices[0].agent.__name__
			result = [f"{agentName} PRE: {pretrain}", e, exp.numFinishedJobs]
			# print(result)
			results.put(result)
			# result = [f"{agentName} PM: {productionMode} OP: {offPolicy} JOBS", e, exp.jobCounter]
			# results.put(result)
	except:
		debug.printCache()
		traceback.print_exc(file=sys.stdout)
		print(agent, e)
		print("Error in experiment :", exp.time)
		sys.exit(0)

	finished.put(True)
	print(f"duration: {agent} PRE {pretrain}: {datetime.now() - startTime}")


def run(numEpisodes):
	print("starting experiment")

	processes = list()
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()

	localConstants.REPEATS = 64
	numEpisodes = int(numEpisodes)
	agentsToTest = [minimalTableAgent, minimalDeepAgent]
	# agentsToTest = [(minimalTableAgent, False), (minimalDeepAgent, True), (minimalDeepAgent, False), ]
	
	for agent in agentsToTest:
		for pretrain in [True, False]:
			for centralised in [True]:
				for _ in range(localConstants.REPEATS):
					processes.append(multiprocessing.Process(target=runThread, args=(len(processes), agent, pretrain, numEpisodes, results, finished)))

	results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodes, assembly=assembleResults, chooseBest=1.0)

	plotting.plotMultiWithErrors("experiment7", title="experiment 7", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)

if __name__ == "__main__":
	setupMultithreading()
	try:
		run(5e1)
	except:
		traceback.print_exc(file=sys.stdout)

		print("ERROR")
