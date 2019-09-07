# from sim import simulation
from sim.simulation import simulation
import sim.constants
import sim.variable
import sim.offloadingPolicy
import sim.debug
import sim.plotting
import sim.tasks

import multiprocessing
import multiprocessing.pool
import collections 
import numpy as np
import matplotlib.pyplot as pp
import time
import warnings
import sys

# import cProfile, pstats, io
import profile
# from pstats import SortKey

def singleDelayedJobLocal(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
	sim.constants.MINIMUM_BATCH = 1
	
	exp = simulation(0, 2, 0)

	sim.constants.JOB_LIKELIHOOD = 0
	# exp.en[0].createNewJob()
	# exp.simulateTime(sim.constants.SIM_TIME)
	exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
	exp.simulateTime(0.25)
	
def doubleDelayedJobLocal(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.MINIMUM_BATCH = 2
	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.PLOT_TD = sim.constants.TD * 2
	
	exp = simulation(0, 2, 0)

	exp.simulateTime(.01)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
	exp.simulateTime(.01)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
	exp.simulateUntilTime(.3)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
	exp.simulateUntilTime(0.6)
	
def differentBatchesLocal(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
	
	exp = simulation(0, 2, 0)

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.MINIMUM_BATCH = 2
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(1)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.MCU_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.PLOT_TD = sim.constants.TD
	sim.constants.RECONFIGURATION_TIME = sim.variable.Constant(0.05)
	exp.simulateTime(0.015)
	for i in range(sim.constants.MINIMUM_BATCH):
		exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated, taskGraph=[sim.tasks.EASY])
		exp.simulateTime(0.015)
		time.sleep(.5)
	# wait until the end	
	if accelerated:
		exp.simulateUntilTime(0.2)
	else:
		exp.simulateUntilTime(0.1)
	for i in range(sim.constants.MINIMUM_BATCH):
		exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated, taskGraph=[sim.tasks.HARD])
		exp.simulateTime(0.015)
		time.sleep(.5)
	# wait until the end
	exp.simulate()



# @staticmethod
def singleBatchLocal(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
	
	exp = simulation(0, 2, 0)

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.MINIMUM_BATCH = 2
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(1)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.MCU_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.PLOT_TD = sim.constants.TD
	sim.constants.RECONFIGURATION_TIME = sim.variable.Constant(0.05)
	exp.simulateTime(0.015)
	for i in range(sim.constants.MINIMUM_BATCH):
		exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
		exp.simulateTime(0.015)
		time.sleep(.5)
	# wait until the end	
	if accelerated:
		exp.simulateUntilTime(0.2)
	else:
		exp.simulateUntilTime(0.1)
	exp.simulate()

def singleBatchRemote(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY
	
	exp = simulation(0, 2, 0)

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.MINIMUM_BATCH = 2
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(10)
	sim.constants.PLOT_TD = sim.constants.TD * 1
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(400, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(100, integer=True)
	sim.constants.RECONFIGURATION_TIME = sim.variable.Constant(0.05)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF
	# exp.en[0].createNewJob()
	# exp.simulateTime(sim.constants.SIM_TIME)
	exp.simulateTime(0.015)
	# time.sleep(0.5)
	for i in range(sim.constants.MINIMUM_BATCH):
		exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
		exp.simulateTime(0.025)
		# time.sleep(0.5)

	exp.simulateUntilTime(0.5)
		

# @staticmethod
def singleDelayedJobPeer(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY
	
	exp = simulation(0, 2, 0)

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.DEFAULT_TASK_GRAPH = [sim.tasks.EASY]

	exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
	exp.simulateTime(sim.constants.PLOT_TD * 150)

def deadlock():
	
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(40, integer=True) # TODO: change back to 4
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF

	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY
	sim.constants.JOB_LIKELIHOOD = 0.01
	sim.constants.DEFAULT_TASK_GRAPH = [sim.tasks.EASY]

	sim.constants.MINIMUM_BATCH = 2
	sim.constants.PLOT_TD = sim.constants.TD * 10
	sim.constants.DISPLAY = False

	exp = simulation(0, 4, 0, hardwareAccelerated=False)

	# exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.simulateTime(1)
	# exp.simulateTime(sim.constants.TD)
	# exp.devices[0].createNewJob(exp.time, hardwareAccelerated=False)
	# exp.simulateTime(sim.constants.PLOT_TD * 150)

	
# @staticmethod
def randomPeerJobs(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY
	sim.constants.DRAW_DEVICES = True
	sim.constants.PLOT_TD = sim.constants.TD

	exp = simulation(0, 4, 0, hardwareAccelerated=accelerated)

	sim.constants.JOB_LIKELIHOOD = 5e-2
	exp.simulateTime(sim.constants.PLOT_TD * 100)
	
# @staticmethod
def randomLocalJobs(accelerated=True):
	sim.constants.SAMPLE_SIZE = sim.variable.Uniform(5,6)
	sim.constants.PLOT_TD = 1e-2
	sim.constants.MINIMUM_BATCH = 5
	sim.constants.JOB_LIKELIHOOD = 10e-2
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY

	exp = simulation(0, 1, 0, hardwareAccelerated=accelerated)
	exp.simulateTime(.5)

def randomJobs(offloadingPolicy=sim.offloadingPolicy.ANYTHING, hw=True):
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = offloadingPolicy
	sim.constants.JOB_LIKELIHOOD = 1e-3 # 2e-3
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(40)
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(10)
	sim.constants.PLOT_TD = 10
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.DRAW_DEVICES = False
	sim.constants.FPGA_IDLE_SLEEP = 0.75
	sim.constants.MINIMUM_BATCH = 5
	sim.constants.DEFAULT_TASK_GRAPH = [sim.tasks.EASY]
	sim.constants.ROUND_ROBIN_TIMEOUT = 1e1

	exp = simulation(0, 1, 0, hardwareAccelerated=hw)
	exp.simulate() #UntilTime(1)

def testRepeatsSeparateThread(i, jobLikelihood, resultsQueue):
	sim.constants.JOB_LIKELIHOOD = jobLikelihood
	
	exp = simulation(0, 4, 0, hardwareAccelerated=False)
	exp.simulateTime(10)

	if not exp.allDone():
		warnings.warn("not all devices done: {}".format(jobLikelihood))

	resultsQueue.put(["Repeat " + str(i), jobLikelihood, (np.average([dev.totalSleepTime for dev in exp.devices]), 0)])
	

def testRepeatsSeparate():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY # sim.offloadingPolicy.LOCAL_ONLY
	sim.constants.MINIMUM_BATCH = 5
	# sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF

	REPEATS = 6

	# results = list()
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)

	# pool = multiprocessing.pool.ThreadPool(12)
	processes = list()
	results = multiprocessing.Queue()
	# numThreads = REPEATS * len(samplesList)
	for i in range(REPEATS):
		# samplesList = range(1, 100, 10)
		
		for jobLikelihood in np.arange(1e-2, 100e-2, 1e-2):
			# for samples in samplesList:
			processes.append(multiprocessing.Process(target=testRepeatsSeparateThread, args=(i, jobLikelihood, results)))
		
	for process in processes: process.start()
	# for process in processes: process.join()
	

	# legends = list()
	graphs = dict()
	for i in range(len(processes)):
		result = results.get()

		graphName, sample, datapoint = result
		if graphName not in graphs.keys():
			graphs[graphName] = dict()
			
		print (graphName, sample, datapoint)
		# legends.append(result[0])
		graphs[graphName][sample] = datapoint

	sim.plotting.plotMultiWithErrors("testRepeats", results=graphs) #, ylim=[0, 5])
	
def testRepeatsThread(name, samples, resultsQueue):
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)

	exp = simulation(0, 1, 0)

	exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=False)
	exp.simulateTime(sim.constants.PLOT_TD * 1500)
	if not exp.allDone():
	
		raise Exception("not all devices done: {}".format(samples))
	# print ('repeat', i, 'done')
	
	resultsQueue.put([name, samples, np.sum(exp.totalDevicesEnergy())])

	# test that sim.constants are still set correctly
	assert(sim.constants.SAMPLE_SIZE.gen() == samples)
	
def testRepeats():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
	sim.constants.MINIMUM_BATCH = 1
	sim.constants.JOB_LIKELIHOOD = 0
	
	REPEATS = 16

	# results = list()
	samplesList = range(1, 100, 10)

	processes = list()
	results = multiprocessing.Queue()
	numThreads = REPEATS * len(samplesList)
	for i in range(REPEATS):
		for samples in samplesList:
			processes.append(multiprocessing.Process(target=testRepeatsThread, args=("Repeats", samples, results)))
	
	for process in processes: process.start()
	for process in processes: process.join()

	sim.plotting.plotMultiWithErrors("testRepeats", results=assembleResults(numThreads, results))

# creates dictionary with (avg, std) for each x for each graph
# takes results as input, 
def assembleResults(resultsQueue, outputQueue, numResults=None):
	# process results into dict
	if numResults is None:
		numResults = resultsQueue.qsize()
	# print ("assembling results", numResults)
	graphs = dict()
	print("")
	for i in range(numResults):
		result = resultsQueue.get()

		sys.stdout.write("\rProgress: {:.2f}%".format((i+1) / numResults * 100.0))
		sys.stdout.flush()

		graphName, sample, datapoint = result
		if graphName not in graphs.keys():
			graphs[graphName] = dict()
			
		if sample not in graphs[graphName].keys():
			graphs[graphName][sample] = list()
		graphs[graphName][sample].append(datapoint)
	
	print("done with experiment")
	# calculate means and averages
	outputGraphs = dict()
	for key, graph in graphs.items():
		# turn each list into a (value, error) tuple
		outputGraphs[key] = dict()
		for x, ylist in graph.items():
			outputGraphs[key][x] = (np.average(ylist), np.std(ylist))
	print ("processed")
	outputQueue.put(outputGraphs)
	print ("after")
	
	# return outputGraphs

def executeMulti(processes, results, finished, numResults=None):
	if numResults is None:
		numResults = len(processes)

	# results consumption thread:
	outputData = multiprocessing.Queue()
	assemble = multiprocessing.Process(target=assembleResults, args=(results, outputData, numResults,))
	assemble.start()

	# process simulation
	currentThreads = 0
	startedThreads = 0
	finishedThreads = 0
	while startedThreads < len(processes):
		while currentThreads < np.min([sim.constants.THREAD_COUNT, len(processes)]):
			processes[startedThreads].start()
			startedThreads += 1
			currentThreads += 1
			# print('started', startedThreads)
			# print('current', currentThreads)
		
		# wait for at least one to finish
		finished.get()
		# processes[finishedThreads].join() #  is not None:	# print ('one down...')
		finishedThreads += 1
		currentThreads -= 1

	print("waiting for assemble...")
	# assemble.join()
	print ("outputdata")

	return outputData.get()

def profileTarget():
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.ANYTHING
	sim.constants.JOB_LIKELIHOOD = 1e-3 # 2e-3
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(40)
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(10)
	sim.constants.PLOT_TD = 10
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.DRAW_DEVICES = False
	sim.constants.FPGA_IDLE_SLEEP = 0.75
	sim.constants.MINIMUM_BATCH = 5
	sim.constants.DEFAULT_TASK_GRAPH = [sim.tasks.EASY]
	sim.constants.ROUND_ROBIN_TIMEOUT = 1e1

	exp = simulation(0, 1, 0, hardwareAccelerated=True)
	exp.simulateTime(100)

def testPerformance():
	profile.run('profileTarget()')

if __name__ == '__main__':
	# for i in range(1, 100, 10):
	# 	print i, exp.simulateAll(i, "latency")


	# singleDelayedJobLocal(False)
	# sim.singleDelayedJobLocal(True)
	# doubleDelayedJobLocal(True)
	# differentBatchesLocal(True)
	# singleDelayedJobPeer(False)
	# singleDelayedJobPeer(True)
	# singleBatchLocal(True)
	# singleBatchLocal(False)
	# singleBatchRemote(False)
	# singleBatchRemote(True)
	# sim.randomPeerJobs(True)
	# randomLocalJobs(False)
	# randomPeerJobs(False)
	
	randomJobs(offloadingPolicy=sim.offloadingPolicy.ROUND_ROBIN, hw=True)
	# testPerformance()
	# profileTarget()
	
	# totalEnergyJobSize()
	# testRepeatsSeparate()
	# totalEnergyJobSize()
	# totalEnergyBatchSize()