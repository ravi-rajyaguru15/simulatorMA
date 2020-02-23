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

numDevices = 4
def runThread(jobLikelihood, fpgaSleepTime, results, finished):
	constants.FPGA_IDLE_SLEEP = fpgaSleepTime
	constants.JOB_LIKELIHOOD = jobLikelihood

	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	exp = SimpleSimulation()

	try:
		# exp.simulateTime(10)
		exp.simulateEpisode()
	except:
		traceback.print_exc(file=sys.stdout)
		print(jobLikelihood, fpgaSleepTime, )
		print("Error in experiment:", jobLikelihood, fpgaSleepTime, exp.getCurrentTime())

	results.put(["FPGA Idle Sleep {}".format(fpgaSleepTime), jobLikelihood, np.sum(exp.totalDevicesEnergy()) / numDevices])
	finished.put(True)

def run():
	print ("starting experiment")
	debug.enabled = False
	constants.DRAW = False
	constants.SAMPLE_SIZE = variable.Gaussian(10, 2)
	constants.SAMPLE_RAW_SIZE = variable.Constant(4, integer=True)
	constants.SAMPLE_PROCESSED_SIZE = variable.Constant(4, integer=True)
	constants.FPGA_POWER_PLAN = powerPolicy.IDLE_TIMEOUT
	constants.OFFLOADING_POLICY = offloadingPolicy.REINFORCEMENT_LEARNING

	processes = list()
	constants.MINIMUM_BATCH = 5
	constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e2
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	constants.REPEATS = 3

	for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
		for fpgaSleepTime in np.arange(0, 1e-0, 2.5e-1):
			for _ in range(constants.REPEATS):
				processes.append(multiprocessing.Process(target=runThread, args=(jobLikelihood, fpgaSleepTime, results, finished)))
	
	results = executeMulti(processes, results, finished)
	
	plotMultiWithErrors("Average Energy", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")