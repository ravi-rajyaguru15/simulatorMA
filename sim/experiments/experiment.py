# from sim import simulation
from sim.simulation import simulation
import sim.constants
import sim.variable
import sim.debug
import sim.plotting

import multiprocessing
import multiprocessing.pool
import collections 
import numpy as np
import matplotlib.pyplot as pp


def singleDelayedJobLocal(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.constants.LOCAL_ONLY
	sim.constants.MINIMUM_BATCH = 1
	
	exp = simulation(0, 2, 0, visualise=True)

	sim.constants.JOB_LIKELIHOOD = 0
	# exp.en[0].createNewJob()
	# exp.simulateTime(sim.constants.SIM_TIME)
	exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
	exp.simulateTime(0.25)
	
# @staticmethod
def singleBatchLocal(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.constants.LOCAL_ONLY
	
	exp = simulation(0, 2, 0, visualise=True)

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.MINIMUM_BATCH = 2
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(1)
	sim.constants.FPGA_POWER_PLAN = sim.constants.FPGA_IMMEDIATELY_OFF
	# exp.en[0].createNewJob()
	# exp.simulateTime(sim.constants.SIM_TIME)
	exp.simulateTime(0.015)
	for i in range(sim.constants.MINIMUM_BATCH):
		exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
		exp.simulateTime(0.015)
	# wait until the end	
	if accelerated:
		exp.simulateUntilTime(0.2)
	else:
		exp.simulateUntilTime(0.1)

def singleBatchRemote(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.constants.PEER_ONLY
	
	exp = simulation(0, 2, 0, visualise=True)

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.MINIMUM_BATCH = 2
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(1)
	sim.constants.FPGA_POWER_PLAN = sim.constants.FPGA_IMMEDIATELY_OFF
	# exp.en[0].createNewJob()
	# exp.simulateTime(sim.constants.SIM_TIME)
	exp.simulateTime(0.015)
	for i in range(sim.constants.MINIMUM_BATCH):
		exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
		exp.simulateTime(0.015)
	exp.simulateUntilTime(0.1)
		

# @staticmethod
def singleDelayedJobPeer(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.constants.PEER_ONLY
	
	exp = simulation(0, 2, 0, visualise=True)

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.DEFAULT_TASK_GRAPH = [sim.tasks.EASY]

	exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
	exp.simulateTime(sim.constants.PLOT_TD * 150)
	
# @staticmethod
def randomPeerJobs(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.constants.PEER_ONLY
	sim.constants.DRAW_DEVICES = True

	exp = simulation(0, 4, 0, visualise=True, hardwareAccelerated=accelerated)

	sim.constants.JOB_LIKELIHOOD = 5e-2
	exp.simulateTime(sim.constants.PLOT_TD * 100)
	
# @staticmethod
def randomLocalJobs(accelerated=True):
	sim.constants.SAMPLE_SIZE = sim.variable.Uniform(5,6)
	sim.constants.PLOT_TD = 1e-2
	sim.constants.MINIMUM_BATCH = 5
	sim.constants.JOB_LIKELIHOOD = 10e-2
	sim.constants.OFFLOADING_POLICY = sim.constants.LOCAL_ONLY

	exp = simulation(0, 1, 0, visualise=True, hardwareAccelerated=accelerated)
	exp.simulateTime(.5)

def testRepeatsSeparateThread(i, samples, resultsQueue):
	# i, samplesList = args
	print ('repeat', i)
	graph = list()
	
	
	# for samples in samplesList:

	sim.constants.SAMPLE_SIZE = sim.variable.Constant(1) # samples)

	exp = simulation(0, 1, 0, visualise=False)

	exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=False)
	exp.simulateTime(sim.constants.PLOT_TD * 1500)
	if not exp.allDone():

		raise Exception("not all devices done: {}".format(samples))
	print ('repeat', i, 'done')
		# graph.append((np.average(thisResult), np.std(thisResult)))
	# return ("Repeat " + str(i), graph)
	resultsQueue.put(["Repeat " + str(i), samples, (np.sum(exp.totalDevicesEnergy()), 0)])
	

def testRepeatsSeparate():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = sim.constants.LOCAL_ONLY
	sim.constants.MINIMUM_BATCH = 1
	sim.constants.JOB_LIKELIHOOD = 0
	
	REPEATS = 16

	# results = list()
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(1) # samples)
	# pool = multiprocessing.pool.ThreadPool(12)
	processes = list()
	results = multiprocessing.Queue()
	numThreads = REPEATS * len(samplesList)
	for i in range(REPEATS):
		samplesList = range(1, 100, 10)
		
		for samples in samplesList:
			processes.append(multiprocessing.Process(target=testRepeatsThread, args=(i, samples, results)))
    	
	for process in processes: process.start()
	for process in processes: process.join()
	

	# legends = list()
	graphs = dict()
	for i in range(numThreads):
		result = results.get()

		graphName, sample, datapoint = result
		if graphName not in graphs.keys():
			graphs[graphName] = dict()
			
		print (graphName, sample, datapoint)
		# legends.append(result[0])
		graphs[graphName][sample] = datapoint

	sim.plotting.plotMultiWithErrors("testRepeats", results=graphs, ylim=[0, 5], show=False, save=True)
	
def testRepeatsThread(name, samples, resultsQueue):
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)

	exp = simulation(0, 1, 0, visualise=False)

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
	sim.constants.OFFLOADING_POLICY = sim.constants.LOCAL_ONLY
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

	sim.plotting.plotMultiWithErrors("testRepeats", results=assembleResults(numThreads, results), save=True)

# creates dictionary with (avg, std) for each x for each graph
def assembleResults(numResults, resultsQueue):
	# process results into dict
	print ("assembling results")
	graphs = dict()
	for i in range(numResults):
		result = resultsQueue.get()

		graphName, sample, datapoint = result
		if graphName not in graphs.keys():
			graphs[graphName] = dict()
			
		if sample not in graphs[graphName].keys():
			graphs[graphName][sample] = list()
		graphs[graphName][sample].append(datapoint)
	
	# calculate means and averages
	outputGraphs = dict()
	for key, graph in graphs.items():
		# turn each list into a (value, error) tuple
		outputGraphs[key] = dict()
		for x, ylist in graph.items():
			outputGraphs[key][x] = (np.average(ylist), np.std(ylist))
			print()
			print(outputGraphs[key][x])
			print(ylist)
			print()
	
	return outputGraphs

if __name__ == '__main__':
	# for i in range(1, 100, 10):
	# 	print i, exp.simulateAll(i, "latency")

	# sim.singleDelayedJobLocal(False)
	# sim.singleDelayedJobLocal(True)
	# sim.singleDelayedJobPeer(False)
	# sim.singleDelayedJobPeer(True)
	# singleBatchLocal(True)
	# singleBatchLocal(False)
	# singleBatchRemote(False)
	# sim.randomPeerJobs(True)
	randomLocalJobs(False)
	# randomPeerJobs(False)
	
	# totalEnergyJobSize()
	# testRepeats()
	# totalEnergyJobSize()
	# totalEnergyBatchSize()
