import multiprocessing
import sys
import traceback
import os
import numpy as np

from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim import debug
from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.plotting import plotMultiWithErrors
from sim.simulations.variable import Gaussian


numDevices = 4


def runThread(jobInterval, results, finished):
	try:
		exp = SimpleSimulation(jobInterval=jobInterval)
		# exp.simulateTime(10)
		# pretrain
		exp.simulateEpisodes(100)
	except:
		traceback.print_exc(file=sys.stdout)
		print("Error in experiment:", jobInterval, exp.time)

	exp.sharedAgent.setProductionMode()
	exp.simulateEpisode()

	results.put(["", jobInterval, exp.numFinishedJobs])
	# results.put(["", jobInterval, np.average([dev.numJobs for dev in exp.devices]) / exp.getCompletedJobs()])
	finished.put(True)


def run():
	print("starting experiment")
	debug.enabled = False

	processes = list()
	# constants.MINIMUM_BATCH = 5
	
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()

	for jobInterval in np.logspace(-3, 1, num=5, base=10.):
		for _ in range(localConstants.REPEATS):
			print(SimpleSimulation())
			processes.append(multiprocessing.Process(target=runThread, args=(jobInterval, results, finished)))
	
	results = executeMulti(processes, results, finished)
	plotMultiWithErrors("Job Interval", results=results, ylabel="Total Jobs", xlabel="Job Interval") # , save=True)

if __name__ == "__main__":
	setupMultithreading()
	try:
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print ("ERROR")