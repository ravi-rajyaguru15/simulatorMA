# from sim import simulation
import sys
print (sys.path)
sys.path.insert(0, ".")
from sim.simulation import simulation
import sim.simulation
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


def randomJobs(offloadingPolicy=sim.offloadingPolicy.ANYTHING, hw=True):
	sim.constants.NUM_DEVICES = 1
	print("random jobs")
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = offloadingPolicy
	sim.constants.JOB_LIKELIHOOD = 9e-3 # 2e-3
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(40)
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(10)
	sim.constants.PLOT_TD = sim.constants.TD * 100
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.DRAW_DEVICES = True
	sim.constants.FPGA_IDLE_SLEEP = 0.075
	if offloadingPolicy == sim.offloadingPolicy.REINFORCEMENT_LEARNING:
		sim.constants.MINIMUM_BATCH = 1e5
	else:
		sim.constants.MINIMUM_BATCH = 5
	sim.constants.DEFAULT_TASK_GRAPH = [sim.tasks.EASY]
	sim.constants.ROUND_ROBIN_TIMEOUT = 1e1

	sim.simulation.current = simulation(hardwareAccelerated=hw)
	print("start simulation")
	sim.simulation.current.simulate() #UntilTime(1)
	# sim.simulation.current.simulateTime(5)

# creates dictionary with (avg, std) for each x for each graph
# takes results as input, 
def assembleResults(resultsQueue, outputQueue, numResults=None):
	# process results into dict
	if numResults is None:
		numResults = resultsQueue.qsize()
	print ("assembling results", numResults)
	graphs = dict()
	# print("")
	normaliseDict = dict()
	for i in range(numResults):
		result = resultsQueue.get()

		sys.stdout.write("\rProgress: {:.2f}%".format((i+1) / numResults * 100.0))
		sys.stdout.flush()

		if len(result) == 4:
			graphName, sample, datapoint, normalise = result
		else:
			graphName, sample, datapoint = result
			normalise = False

		if graphName not in graphs.keys():
			graphs[graphName] = dict()
			normaliseDict[graphName] = normalise
			
		if sample not in graphs[graphName].keys():
			graphs[graphName][sample] = list()
			# print ("creating list", graphName, sample)

		graphs[graphName][sample].append(datapoint)

	# normalise if required
	print()
	print("normalise:", normaliseDict)
	print("find max")
	# print("graphs", graphs)
	# for key in graphs:
	# 	print()
	# 	print(key)
	# 	print(graphs[key])


	print()
	maxDict = dict()
	for name in graphs:
		if not normaliseDict[name]: continue

		graphDict = graphs[name]
		maxDict[name] = 0
		for sample in graphDict:
			# print(sample, graphDict[sample])
			maxDict[name] = np.max([maxDict[name], np.max(np.abs(graphDict[sample]))])
			# graphDict[sample] = np.array(graphDict[sample]) / 
	
	print('max', maxDict)
	for name in maxDict:
		maximum = maxDict[name]
		for sample in graphs[name]:
			graphs[name][sample] /= maximum

	
	print("done with experiment")
	# calculate means and averages
	outputGraphs = dict()
	for key, graph in graphs.items():
		# turn each list into a (value, error) tuple
		outputGraphs[key] = dict()
		for x, ylist in graph.items():
			# print()
			# print(ylist)
			outputGraphs[key][x] = (np.average(ylist), np.std(ylist))
			# print(outputGraphs[key][x])
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


if __name__ == '__main__':
	# for i in range(1, 100, 10):
	# 	print i, exp.simulateAll(i, "latency")

	# sim.constants.DRAW_DEVICES = True
	# testPerformance()

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
	# testActions()
	
	randomJobs(offloadingPolicy=sim.offloadingPolicy.REINFORCEMENT_LEARNING, hw=True)
	# testPerformance()
	# profileTarget()
	
	# totalEnergyJobSize()
	# testRepeatsSeparate()
	# totalEnergyJobSize()
	# totalEnergyBatchSize()
