import multiprocessing

import sys
import traceback
from multiprocessing import freeze_support

import sim
from sim import debug, counters, plotting
from sim.devices.components.powerPolicy import IDLE_TIMEOUT
from sim.experiments.experiment import executeMulti, assembleResultsBasic
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.offloading.offloadingPolicy import REINFORCEMENT_LEARNING
from sim.simulations import simulationResults
from sim.simulations.SimpleSimulation import SimpleSimulation

sim.simulations.constants.NUM_DEVICES = 1


def runThread(agent, numTicks, results, finished, histories):
	exp = SimpleSimulation(agentClass=agent)
	exp.reset()
	timeOffsets = dict()
	previousTime = dict()
	for dev in exp.devices:
		timeOffsets[dev] = 0
		previousTime[dev] = 0

	try:
		for i in range(numTicks):
			if exp.finished:
				for dev in exp.devices:
					timeOffsets[dev] += dev.currentTime.current
				exp.reset()
			# for i in range():
			exp.simulateTick()

			for dev in exp.devices:
				currentTime = timeOffsets[dev] + dev.currentTime.current
				results.put(["%s Power" % dev, previousTime[dev], dev.latestPower])
				print('\n', previousTime[dev], dev.latestPower)
				previousTime[dev] = currentTime
				print('\n', currentTime, dev.latestPower)
				results.put(["%s Power" % dev, currentTime, dev.latestPower])
	except:
		traceback.print_exc(file=sys.stdout)
		print(agent, i)
		print("Error in experiment ̰:", exp.time)
		debug.printCache(200)
		sys.exit(0)

	finished.put(True)
	assert simulationResults.learningHistory is not None
	histories.put(simulationResults.learningHistory)
	print("\nsaving history", simulationResults.learningHistory, '\nr')

	print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)

	exp.sharedAgent.printModel()

def run():
	print("starting experiment")
	debug.enabled = False
	debug.learnEnabled = False
	debug.infoEnabled = False

	sim.simulations.constants.DRAW = False
	sim.simulations.constants.FPGA_POWER_PLAN = IDLE_TIMEOUT
	sim.simulations.constants.FPGA_IDLE_SLEEP = 5
	sim.simulations.constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
	# sim.simulations.constants.TOTAL_TIME = 1e3
	sim.simulations.constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e0
	sim.simulations.constants.MAX_JOBS = 3

	processes = list()
	sim.simulations.constants.MINIMUM_BATCH = 1e7

	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	histories = multiprocessing.Queue()
	sim.simulations.constants.REPEATS = 1

	# for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
	# 	for roundRobin in np.arange(1e0, 1e1, 2.5):
	numTicks = int(1e3)
	agentsToTest = [minimalAgent] # , lazyAgent]
	for agent in agentsToTest: # [minimalAgent, lazyAgent]:
		for _ in range(sim.simulations.constants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(agent, numTicks, results, finished, histories)))

	results = executeMulti(processes, results, finished, assembly=assembleResultsBasic, numResults=sim.simulations.constants.NUM_DEVICES * sim.simulations.constants.REPEATS * numTicks * 2)

	plotting.plotMulti("Device Power", results=results, ylabel="Reward", xlabel="Episode #")  # , save=True)
	# plotting.plotAgentHistory(histories.get())


if __name__ == "__main__":
	freeze_support()
	try:
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print("ERROR")