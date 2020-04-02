import multiprocessing
import sys
import traceback

import numpy as np

from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.plotting import plotMultiWithErrors
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation


def runThread(jobInterval, fpgaSleepTime, numEpisodes, results, finished):
	exp = SimpleSimulation(numDevices=4, maxJobs=maxJobs)
	exp.setFpgaIdleSleep(fpgaSleepTime)
	exp.scenario.setInterval(jobInterval)
	print('interval', exp.scenario.timeInterval.mean)
	exp.setBatterySize(1e1)

	try:
		for i in range(numEpisodes):
			# exp.simulateTime(10)
			exp.simulateEpisode()
			results.put(["FPGA Idle Sleep {} Interval {}".format(fpgaSleepTime, jobInterval), i, exp.getCurrentTime()])
	except:
		traceback.print_exc(file=sys.stdout)
		print(jobInterval, fpgaSleepTime, )
		print("Error in experiment:", jobInterval, fpgaSleepTime, exp.getCurrentTime())

	finished.put(True)


def run():
	print("starting experiment")

	processes = list()

	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	numEpisodes = int(1e1)

	for jobInterval in [0.1, 1]: #, 10]: #np.arange(0.1, 1., 0.3):
		# for fpgaSleepTime in [1e-6, 1e-3, 2e-3, 1e-2]: #, 1]:# np.arange(0, 1e-0, 5e-1):
		for _ in range(localConstants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(jobInterval, 1e-3, numEpisodes, results, finished)))

	results = executeMulti(processes, results, finished, numResults=numEpisodes * len(processes))

	plotMultiWithErrors("Episode Duration", results=results) # , save=True)


if __name__ == '__main__':
	try:
		setupMultithreading()
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print ("ERROR")