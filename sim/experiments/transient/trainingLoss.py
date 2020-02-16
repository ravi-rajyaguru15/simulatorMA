import multiprocessing
import sys
import traceback

from sim.simulation import simulation

import sim.debug
import sim.experiments.experiment
import sim.learning.offloadingDecision
import sim.plotting
import sim.simulations.constants
import sim.simulations.variable

sim.simulations.constants.NUM_DEVICES = 4
numJobs = int(1e2)
def runThread(results, finished):
	exp = simulation(hardwareAccelerated=True)

	try:
		for i in range(numJobs):
			exp.simulateUntilJobDone()
			results.put(["Loss", exp.completedJobs, sim.learning.offloadingDecision.offloadingDecision.learningAgent.loss, True])
			results.put(["Reward", exp.completedJobs, sim.learning.offloadingDecision.offloadingDecision.learningAgent.latestReward, True])
			results.put(["Action", exp.completedJobs, sim.learning.offloadingDecision.offloadingDecision.learningAgent.latestAction, True])
			results.put(["MAE", exp.completedJobs, sim.learning.offloadingDecision.offloadingDecision.learningAgent.latestMAE, True])
			results.put(["MeanQ", exp.completedJobs, sim.learning.offloadingDecision.offloadingDecision.learningAgent.latestMeanQ, True])
	except:
		traceback.print_exc(file=sys.stdout)
		sys.exit(0)
		print("Error in experiment:", exp.time)

	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.simulations.constants.DRAW = False
	sim.simulations.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.simulations.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
	# sim.constants.TOTAL_TIME = 1e3

	processes = list()
	sim.simulations.constants.MINIMUM_BATCH = 1e5
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.simulations.constants.REPEATS = 1

	# for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
	# 	for roundRobin in np.arange(1e0, 1e1, 2.5):
	for _ in range(sim.simulations.constants.REPEATS):
		processes.append(multiprocessing.Process(target=runThread, args=(results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished, numResults=numJobs * sim.simulations.constants.REPEATS * 5)
	
	sim.plotting.plotMultiWithErrors("Learning Loss", results=results, ylabel="Loss", xlabel="Job #") # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")