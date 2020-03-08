import multiprocessing
import sys
import traceback
import os
import numpy as np

from sim.simulations.SimpleSimulation import SimpleSimulation
from sim import debug
from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.plotting import plotMultiWithErrors
from sim.simulations.variable import Gaussian


numDevices = 4


def runThread(exp, jobInterval, results, finished):
	try:
		exp = SimpleSimulation(jobInterval=Gaussian(jobInterval, 1))
		# exp.simulateTime(10)
		exp.simulateEpisode()
	except:
		traceback.print_exc(file=sys.stdout)
		print("Error in experiment:", jobInterval, exp.time)

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
	REPEATS = 4

	for jobInterval in np.arange(1, 1e2, 1e1):
		for _ in range(REPEATS):
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