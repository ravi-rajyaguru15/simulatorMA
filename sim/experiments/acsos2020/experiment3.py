import multiprocessing
import sys
import traceback
import os
import numpy as np

from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.state.extendedSystemState import extendedSystemState
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim import debug
from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.plotting import plotMultiWithErrors
from sim.simulations.variable import Gaussian
from sim.tasks.tasks import HARD

numDevices = 4


def runThread(numTrain, numTest, agent, maxJobs, results, finished):
	exp = None
	try:
		# pretrain

		exp = SimpleSimulation(numDevices=numDevices, maxJobs=maxJobs, agentClass=agent, tasks=[HARD], systemStateClass=extendedSystemState, jobInterval=1)
		exp.setBatterySize(1e-1)
		exp.setFpgaIdleSleep(1e-3)
		exp.simulateEpisodes(int(numTrain))
	except:
		traceback.print_exc(file=sys.stdout)
		if exp is not None:
			print("Error in experiment:", maxJobs, exp.time)

	exp.sharedAgent.setProductionMode()

	for i in range(int(numTest)):
		exp.simulateEpisode(int(numTrain) + i)
		results.put(["Agent %s" % exp.sharedAgent.__name__, maxJobs, exp.numFinishedJobs])
	# results.put(["", jobInterval, np.average([dev.numJobs for dev in exp.devices]) / exp.getCompletedJobs()])
	finished.put(True)


def run():
	print("starting experiment")
	debug.enabled = False

	processes = list()
	# constants.MINIMUM_BATCH = 5

	localConstants.REPEATS = 1
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	numtrain = 1e3
	numtest = int(1e1)
	for agent in [lazyTableAgent, minimalTableAgent]:
	# for agent in [lazyTableAgent]:
		# for maxJobs in np.linspace(2, 100, num=10):
		# for maxJobs in [256]:
		for maxJobs in np.logspace(0, 9, base=2, num=10):
			for _ in range(localConstants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(numtrain, numtest, agent, int(maxJobs), results, finished)))
	
	results = executeMulti(processes, results, finished, numResults=len(processes) * numtest)
	plotMultiWithErrors("Max Jobs in Queue", results=results, ylabel="Total Jobs", xlabel="Max Queue") # , save=True)

if __name__ == "__main__":
	setupMultithreading()
	try:
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print ("ERROR")