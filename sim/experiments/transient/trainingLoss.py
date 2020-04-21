import multiprocessing
import sys
import traceback

from sim.experiments.experiment import executeMulti
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.plotting import plotMultiWithErrors
from sim.simulations.SimpleSimulation import SimpleSimulation

numJobs = int(1e5)
def runThread(results, finished):
	exp = SimpleSimulation(numDevices=4, maxJobs=100, reconsiderBatches=False, systemStateClass=minimalSystemState, agentClass=minimalTableAgent)
	exp.setFpgaIdleSleep(1e-2)
	exp.setBatterySize(1e6)

	try:
		for i in range(numJobs):
			exp.simulateUntilJobDone()
			results.put(["Loss", exp.completedJobs, exp.sharedAgent.latestLoss, False])
			# results.put(["Reward", exp.completedJobs, exp.sharedAgent.latestReward, True])
			# results.put(["Action", exp.completedJobs, exp.sharedAgent.latestAction, True])
			# results.put(["MAE", exp.completedJobs, exp.sharedAgent.latestMAE, True])
			# results.put(["MeanQ", exp.completedJobs, exp.sharedAgent.latestMeanQ, True])
	except:
		traceback.print_exc(file=sys.stdout)
		sys.exit(0)
		print("Error in experiment:", exp.time)

	finished.put(True)

def run():
	print ("starting experiment")
	processes = list()
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	REPEATS = 1

	# for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
	# 	for roundRobin in np.arange(1e0, 1e1, 2.5):
	for _ in range(REPEATS):
		processes.append(multiprocessing.Process(target=runThread, args=(results, finished)))
	
	results = executeMulti(processes, results, finished, numResults=numJobs * REPEATS * 1)
	
	plotMultiWithErrors("Learning Behaviour", results=results, ylabel="Normalised Quantities", xlabel="Job #") # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")