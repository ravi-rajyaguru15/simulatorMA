import multiprocessing
import sys
import traceback

import numpy as np

from sim import debug
from sim.devices.components import powerPolicy
from sim.experiments.experiment import executeMulti
from sim.offloading import offloadingPolicy
from sim.plotting import plotMultiWithErrors
from sim.simulations import constants, variable
from sim.simulations.SimpleSimulation import SimpleSimulation

def runThread(exp, jobInterval, fpgaSleepTime, results, finished):
	exp.setFpgaIdleSleep(fpgaSleepTime)
	exp.setBatterySize(1e2)

	try:
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
	REPEATS = 3

	for jobInterval in np.arange(1, 1e1, 1):
		for fpgaSleepTime in np.arange(0, 1e-0, 2.5e-1):
			for _ in range(REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(SimpleSimulation(numDevices=4), jobInterval, fpgaSleepTime, results, finished)))
	
	results = executeMulti(processes, results, finished)
	
	plotMultiWithErrors("Average Energy", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")