import multiprocessing
import sys
import traceback
import os
import numpy as np

from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim import debug
from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.plotting import plotMultiWithErrors
from sim.simulations.variable import Gaussian


numDevices = 4


def runThread(agent, maxJobs, results, finished):
	try:
		# pretrain

		exp = SimpleSimulation(maxJobs=maxJobs, agentClass=agent)
		exp.simulateEpisodes(100)
	except:
		traceback.print_exc(file=sys.stdout)
		print("Error in experiment:", maxJobs, exp.time)

	exp.sharedAgent.setProductionMode()
	exp.simulateEpisode()

	results.put(["Agent %s" % exp.sharedAgent.__name__, maxJobs, exp.numFinishedJobs])
	# results.put(["", jobInterval, np.average([dev.numJobs for dev in exp.devices]) / exp.getCompletedJobs()])
	finished.put(True)


def run():
	print("starting experiment")
	debug.enabled = False

	processes = list()
	# constants.MINIMUM_BATCH = 5
	
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()

	for agent in [lazyTableAgent, minimalTableAgent]:
		for maxJobs in np.linspace(2, 100, num=10):
			for _ in range(localConstants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(agent, int(maxJobs), results, finished)))
	
	results = executeMulti(processes, results, finished)
	plotMultiWithErrors("Job Interval", results=results, ylabel="Total Jobs", xlabel="Job Interval") # , save=True)

if __name__ == "__main__":
	setupMultithreading()
	try:
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print ("ERROR")