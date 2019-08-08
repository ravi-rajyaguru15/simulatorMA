from sim import sim
import constants
import variable
import numpy as np
import matplotlib.pyplot as pp
import debug

import multiprocessing
import multiprocessing.pool
import collections 

import plotting

REPEATS = 3

def singleDelayedJobLocal(accelerated=True):
	constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
	constants.MINIMUM_BATCH = 1
	
	simulation = sim(0, 2, 0, visualise=True)

	constants.JOB_LIKELIHOOD = 0
	# simulation.en[0].createNewJob()
	# simulation.simulateTime(constants.SIM_TIME)
	simulation.simulateTime(constants.PLOT_TD * 10)
	simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=accelerated)
	simulation.simulateTime(0.25)
	
@staticmethod
def singleBatchLocal(accelerated=True):
	constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
	
	simulation = sim(0, 2, 0, visualise=True)

	constants.JOB_LIKELIHOOD = 0
	constants.MINIMUM_BATCH = 2
	# simulation.en[0].createNewJob()
	# simulation.simulateTime(constants.SIM_TIME)
	simulation.simulateTime(constants.PLOT_TD * 10)
	for i in range(constants.MINIMUM_BATCH):
		simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=accelerated)
		simulation.simulateTime(0.1)
	simulation.simulateTime(0.25)
		

@staticmethod
def singleDelayedJobPeer(accelerated=True):
	constants.OFFLOADING_POLICY = constants.PEER_ONLY
	
	simulation = sim(0, 2, 0, visualise=True)

	constants.JOB_LIKELIHOOD = 0
	constants.DEFAULT_TASK_GRAPH = [tasks.EASY]

	simulation.simulateTime(constants.PLOT_TD * 10)
	simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=accelerated)
	simulation.simulateTime(constants.PLOT_TD * 150)
	
@staticmethod
def randomPeerJobs(accelerated=True):
	constants.OFFLOADING_POLICY = constants.PEER_ONLY
	
	simulation = sim(0, 4, 0, visualise=True, hardwareAccelerated=accelerated)

	constants.JOB_LIKELIHOOD = 5e-2
	simulation.simulateTime(constants.PLOT_TD * 100)
	
@staticmethod
def randomLocalJobs(accelerated=True):
	constants.SAMPLE_SIZE = variable.Uniform(5,6)
	constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
	
	simulation = sim(0, 2, 0, visualise=True)

	constants.JOB_LIKELIHOOD = 5e-2
	simulation.simulateTime(constants.PLOT_TD * 100)

def totalEnergyJobSizeThread(name, hw, samples, results):
	constants.SAMPLE_SIZE = variable.Constant(samples)

	simulation = sim(0, 1, 0, visualise=False)

	simulation.simulateTime(0.1)
	simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=hw)
	simulation.simulateTime(10)
	if not simulation.allDone():
		raise Exception("not all devices done: {}".format(samples))

	results.put([name, samples, np.sum(simulation.totalDevicesEnergy())])


def totalEnergyJobSize():
	print ("starting experiment")
	debug.enabled = False
	constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
	constants.MINIMUM_BATCH = 1
	constants.JOB_LIKELIHOOD = 0
	
	processes = list()
	hwOptions = [True, False]
	results = multiprocessing.Queue()
	samplesList = range(1, 1000, 10)

	for hw in hwOptions:
		for samples in samplesList:
			for i in range(REPEATS):				
				processes.append(multiprocessing.Process(target=totalEnergyJobSizeThread, args=("HW Acceleration {}".format(hw), hw, samples, results)))
	
	for process in processes: process.start()
	# for process in processes: process.join()

	plotting.plotMultiWithErrors("totalEnergyJobSize", results=assembleResults(len(processes), results), save=True)

def testRepeatsSeparateThread(i, samples, resultsQueue):
	# i, samplesList = args
	print ('repeat', i)
	graph = list()
	
	
	# for samples in samplesList:

	constants.SAMPLE_SIZE = variable.Constant(1) # samples)

	simulation = sim(0, 1, 0, visualise=False)

	simulation.simulateTime(constants.PLOT_TD * 10)
	simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=False)
	simulation.simulateTime(constants.PLOT_TD * 1500)
	if not simulation.allDone():
		raise Exception("not all devices done: {}".format(samples))

	print ('repeat', i, 'done')
		# graph.append((np.average(thisResult), np.std(thisResult)))
	# return ("Repeat " + str(i), graph)
	resultsQueue.put(["Repeat " + str(i), samples, (np.sum(simulation.totalDevicesEnergy()), 0)])
	

def testRepeatsSeparate():
	print ("starting experiment")
	debug.enabled = False
	constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
	constants.MINIMUM_BATCH = 1
	constants.JOB_LIKELIHOOD = 0
	
	REPEATS = 16

	# results = list()
	constants.SAMPLE_SIZE = variable.Constant(1) # samples)
	samplesList = range(1, 100, 10)

	# pool = multiprocessing.pool.ThreadPool(12)
	processes = list()
	results = multiprocessing.Queue()
	numThreads = REPEATS * len(samplesList)
	for i in range(REPEATS):
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

	plotting.plotMultiWithErrors("testRepeats", results=graphs, ylim=[0, 5], show=False, save=True)
	
def testRepeatsThread(name, samples, resultsQueue):
	constants.SAMPLE_SIZE = variable.Constant(samples)

	simulation = sim(0, 1, 0, visualise=False)

	simulation.simulateTime(constants.PLOT_TD * 10)
	simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=False)
	simulation.simulateTime(constants.PLOT_TD * 1500)
	if not simulation.allDone():
		raise Exception("not all devices done: {}".format(samples))

	# print ('repeat', i, 'done')
	
	resultsQueue.put([name, samples, np.sum(simulation.totalDevicesEnergy())])

	# test that constants are still set correctly
	assert(constants.SAMPLE_SIZE.gen() == samples)
	
def testRepeats():
	print ("starting experiment")
	debug.enabled = False
	constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
	constants.MINIMUM_BATCH = 1
	constants.JOB_LIKELIHOOD = 0
	
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

	plotting.plotMultiWithErrors("testRepeats", results=assembleResults(numThreads, results), save=True)

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
	
	return outputGraphs

if __name__ == '__main__':
	# for i in range(1, 100, 10):
	# 	print i, simulation.simulateAll(i, "latency")

	# sim.singleDelayedJobLocal(False)
	# sim.singleDelayedJobLocal(True)
	# sim.singleDelayedJobPeer(False)
	# sim.singleDelayedJobPeer(True)
	# sim.randomPeerJobs(True)
	# sim.randomPeerJobs(False)
	# sim.singleBatchLocal(False)
	
	# totalEnergyJobSize()
	# testRepeats()
	totalEnergyJobSize()
