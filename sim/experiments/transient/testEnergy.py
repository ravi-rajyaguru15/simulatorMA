import multiprocessing

import sys
import time
import traceback
from multiprocessing import freeze_support

from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti, assembleResultsBasic
from sim.experiments.scenario import REGULAR_SCENARIO_RANDOM
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation


def runThread(agent, numTicks, numDevices, results, finished, histories):
	exp = SimpleSimulation(numDevices=numDevices, scenarioTemplate=REGULAR_SCENARIO_RANDOM, jobInterval=10, agentClass=agent)
	exp.setBatterySize(1e4)
	exp.reset()
	timeOffsets = dict()
	previousTime = dict()
	currentEnergy = dict()
	for dev in exp.devices:
		timeOffsets[dev] = 0
		currentEnergy[dev] = dev.energyLevel
		previousTime[dev] = 0
		dev.latestPower = None


	i = None
	try:
		for i in range(numTicks):
			if exp.finished:
				for dev in exp.devices:
					timeOffsets[dev] += dev.currentTime.current
				exp.reset()
			# for i in range():
			usages = exp.simulateTick()
			if usages == []:
				usages = [(0,0),(0,0)]
			for duration, power in usages:
				currentTime = previousTime[exp.latestDevice] + duration
				results.put(["%s Power" % exp.latestDevice, previousTime[exp.latestDevice], power * 1e3])
				previousTime[exp.latestDevice] = currentTime
				results.put(["%s Power" % exp.latestDevice, currentTime, power * 1e3])
			time.sleep(0.2)
	except:
		traceback.print_exc(file=sys.stdout)
		print(agent, i)
		print("Error in experiment ̰:", exp.time)
		debug.printCache(200)
		sys.exit(0)

	finished.put(True)
	# assert simulationResults.learningHistory is not None
	# histories.put(simulationResults.learningHistory)
	# print("\nsaving history", simulationResults.learningHistory, '\nr')

	print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)

	# exp.sharedAgent.printModel()

def run():
	print("starting experiment")
	debug.settings.enabled = False
	debug.settings.learnEnabled = False
	debug.settings.infoEnabled = False

	processes = list()
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	histories = multiprocessing.Queue()

	numDevices = 2
	numTicks = int(1e1)
	agentsToTest = [minimalTableAgent] # , lazyAgent]
	for agent in agentsToTest: # [minimalAgent, lazyAgent]:
		for _ in range(localConstants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(agent, numTicks, numDevices, results, finished, histories)))

	results = executeMulti(processes, results, finished, assembly=assembleResultsBasic, numResults=localConstants.REPEATS * numTicks * 2)

	plotting.plotMulti("Device Power", results=results, ylabel="Power (in mW)", xlabel="Tick #") #, ylim=[0, 0.1])  # , save=True)
	# plotting.plotAgentHistory(histories.get())


if __name__ == "__main__":
	freeze_support()
	try:
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print("ERROR")