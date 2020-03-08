import multiprocessing
import sys
import traceback
import os
import numpy as np

from sim import debug
from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.experiments.scenario import REGULAR_SCENARIO_RANDOM
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.plotting import plotMultiWithErrors
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.simulations.variable import Gaussian


def runThread(numEpisodes, jobInterval, agent, results, finished):
	try:
		exp = SimpleSimulation(scenarioTemplate=REGULAR_SCENARIO_RANDOM, jobInterval=jobInterval, agentClass=agent)
		exp.setFpgaIdleSleep(10)
		exp.setBatterySize(1e1)
		for i in range(numEpisodes):
			exp.simulateEpisode()
			results.put(["%s %d s" % (exp.sharedAgent, jobInterval), i, exp.numFinishedJobs])

	except:
		traceback.print_exc(file=sys.stdout)
		print("Error in experiment:", jobInterval, exp.getCurrentTime())

	finished.put(True)


def run():
	print("starting experiment")
	debug.enabled = False

	processes = list()
	# constants.MINIMUM_BATCH = 5
	
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	numEpisodes = int(1e3)
	intervals = np.logspace(start=0, stop=3, base=2., num=4)
	print(intervals)

	for jobInterval in intervals:
		for agent in [minimalAgent, lazyAgent]:
			for _ in range(localConstants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(numEpisodes, jobInterval, agent, results, finished)))
	
	results = executeMulti(processes, results, finished, numResults=numEpisodes*len(processes))
	plotMultiWithErrors("Job Interval", results=results, ylabel="Total Jobs", xlabel="Episode #") # , save=True)


if __name__ == "__main__":
	setupMultithreading()
	try:
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print ("ERROR")