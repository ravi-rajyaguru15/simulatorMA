import multiprocessing
import sys
import traceback

import numpy as np

from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.plotting import plotMultiWithErrors
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation


def runThread(jobInterval, fpgaSleepTime, numEpisodes, results, finished):
	exp = SimpleSimulation(numDevices=4)
	exp.scenario.setInterval(1)
	exp.setFpgaIdleSleep(fpgaSleepTime)
	exp.setBatterySize(1e1)

	try:
		for i in range(numEpisodes):
			# exp.simulateTime(10)
			exp.simulateEpisode()
	except:
		traceback.print_exc(file=sys.stdout)
		print(jobInterval, fpgaSleepTime, )
		print("Error in experiment:", jobInterval, fpgaSleepTime, exp.getCurrentTime())

	results.put(["FPGA Idle Sleep {}".format(fpgaSleepTime), jobInterval, np.sum(exp.totalDevicesEnergy()) / exp.getNumDevices()])
	finished.put(True)


def run():
	print ("starting experiment")

	processes = list()

	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	numEpisodes = int(1e2)

	for jobInterval in np.arange(1, 1e1, 1):
		for fpgaSleepTime in np.arange(0, 1e-0, 2.5e-1):
			for _ in range(localConstants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(jobInterval, fpgaSleepTime, numEpisodes, results, finished)))

	results = executeMulti(processes, results, finished, numResults=numEpisodes * len(processes))

	plotMultiWithErrors("Average Energy", results=results) # , save=True)


if __name__ == '__main__':
	try:
		setupMultithreading()
		run()
	except:
		traceback.print_exc(file=sys.stdout)

		print ("ERROR")