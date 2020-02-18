import multiprocessing
import sys
import traceback

import sim.debug as debug
import sim.simulations.constants as constants
# from sim.learning.state.binarySystemState import binarySystemState
from experiments.experiment import executeMulti
from plotting import plotMultiWithErrors
from sim.learning.agent.minimalAgent import minimalAgent
from offloading.offloadingDecision import offloadingDecision
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.offloading.offloadingPolicy import *
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation

def runThread(index, results, finished):
	exp = Simulation(minimalSystemState, offloadingDecision, minimalAgent)

	# just run each thread to see if it crashes
	# while True:
	for i in range(1):
		try:
			exp.simulateEpisode()
		except Exception:
			print()
			print('-' * 100)
			print("error found!")
			print('-' * 100)
			print("number of successful episodes:", exp.episodeNumber)
			print(sys.exc_info())
			traceback.print_stack()
			sys.exit(-1)
		# print("end of episode!", exp.time)

	results.put(["test", index, exp.episodeNumber])
	finished.put(True)
	# print("Experiment done!", exp.time)



if __name__ == '__main__':
	print("testing simple simulation")
	constants.NUM_DEVICES = 1
	constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e1
	constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
	debug.enabled = False
	constants.DRAW_DEVICES = False

	processes = []
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()

	# for i in range(multiprocessing.cpu_count()-1):
	for i in range(100):
		processes.append(multiprocessing.Process(target=runThread, args=(i, results, finished)))

	results = executeMulti(processes, results, finished)
	plotMultiWithErrors("StabilityTest", results=results)

	# np.set_printoptions(threshold=sys.maxsize, suppress=True)
	# sim.learning.offloadingDecision.sharedAgent.printModel()
