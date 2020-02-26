import multiprocessing
import sys
import traceback

import numpy as np

from sim import debug
from sim.devices.components import powerPolicy
from sim.experiments.experiment import executeMulti
from sim.offloading import offloadingPolicy
from sim.plotting import plotMultiWithErrors
from sim.simulations import constants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.simulations.variable import Gaussian

numDevices = 4
def runThread(jobInterval, results, finished):
	exp = SimpleSimulation(jobInterval=Gaussian(jobInterval, 1))

	try:
		# exp.simulateTime(10)
		exp.simulateEpisode()
	except:
		traceback.print_exc(file=sys.stdout)
		print("Error in experiment:", jobInterval, exp.getCurrentTime())

	print("result:", ["", jobInterval, np.average([dev.getAveragePower() for dev in exp.devices])])
	results.put(["", jobInterval, np.average([dev.getAveragePower() for dev in exp.devices])])
	# results.put(["", jobInterval, np.average([dev.numJobs for dev in exp.devices]) / exp.getCompletedJobs()])
	finished.put(True)

def run():
	print("starting experiment")
	debug.enabled = False

	processes = list()
	constants.MINIMUM_BATCH = 5
	
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	REPEATS = 2

	for jobInterval in np.arange(1, 2e1, 1e1):
		for _ in range(REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(jobInterval, results, finished)))
	
	results = executeMulti(processes, results, finished)
	plotMultiWithErrors("Average Power vs Job Interval", results=results, ylabel="Average Device Power", xlabel="Job Interval") # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")