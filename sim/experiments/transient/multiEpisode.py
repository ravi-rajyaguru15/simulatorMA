import multiprocessing
import sys
import traceback

from sim.simulation import simulation

import sim.counters
import sim.debug
import sim.experiments.experiment
import offloading.offloadingDecision
import sim.plotting
import sim.simulations.constants
import sim.simulations.results
import sim.simulations.variable
import sim.tasks.job

sim.simulations.constants.NUM_DEVICES = 1

def runThread(numEpisodes, results, finished, histories):
	exp = simulation(hardwareAccelerated=True)
	sim.simulations.current = exp

	try:
		for e in range(numEpisodes):
			exp.simulateEpisode()
			results.put(["Duration", e, exp.time.current])
			results.put(["Episode reward", e, offloading.offloadingDecision.sharedAgent.episodeReward])
			results.put(["Overall reward", e, offloading.offloadingDecision.sharedAgent.totalReward])
	except:
		traceback.print_exc(file=sys.stdout)
		print("Error in experiment:", exp.time)
		sys.exit(0)

	finished.put(True)
	histories.put(sim.simulations.results.learningHistory)
	# print("\nsaving history", sim.results.learningHistory, '\nr')

	print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.simulations.constants.DRAW = False
	sim.simulations.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.simulations.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
	# sim.constants.TOTAL_TIME = 1e3
	sim.simulations.constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e-2


	processes = list()
	sim.simulations.constants.MINIMUM_BATCH = 1e5
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	histories = multiprocessing.Queue()
	sim.simulations.constants.REPEATS = 1

	# for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
	# 	for roundRobin in np.arange(1e0, 1e1, 2.5):
	numEpisodes = int(1e6)
	for _ in range(sim.simulations.constants.REPEATS):
		processes.append(multiprocessing.Process(target=runThread, args=(numEpisodes, results, finished, histories)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished, numResults=numEpisodes * sim.simulations.constants.REPEATS * 3)
	
	sim.plotting.plotMultiWithErrors("Episode duration", results=results, ylabel="Reward", xlabel="Episode #") # , save=True)
	sim.plotting.plotAgentHistory(histories.get())

if __name__ == "__main__":
	try:
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print("ERROR")