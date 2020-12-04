

# TODO: initial sleep mcu!
# TODO: sleep mcu during reconfiguration!
import math
import time
from sys import stdout

import scipy
import scipy.stats

from sim import debug, counters
from sim.devices.components.powerPolicy import IDLE_TIMEOUT
from sim.learning.agent.minimalAgent import minimalAgent
from sim.offloading.offloadingPolicy import ANYTHING, REINFORCEMENT_LEARNING
from sim.simulations import constants
from sim.simulations.variable import Constant
from sim.tasks.job import job
from sim.tasks.tasks import EASY
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation

import numpy as np
import multiprocessing

def randomJobs(offloadingPolicy=ANYTHING, hw=True):
	constants.NUM_DEVICES = 1
	print("random jobs")
	debug.enabled = True
	constants.OFFLOADING_POLICY = offloadingPolicy
	constants.JOB_LIKELIHOOD = 9e-3  # 2e-3
	constants.SAMPLE_RAW_SIZE = Constant(40)
	constants.SAMPLE_SIZE = Constant(10)
	constants.PLOT_SKIP = 1
	constants.FPGA_POWER_PLAN = IDLE_TIMEOUT
	constants.DRAW_DEVICES = True
	constants.FPGA_IDLE_SLEEP = 0.075
	if offloadingPolicy == REINFORCEMENT_LEARNING:
		constants.MINIMUM_BATCH = 1e5
	else:
		constants.MINIMUM_BATCH = 5
	constants.DEFAULT_TASK_GRAPH = [EASY]
	constants.ROUND_ROBIN_TIMEOUT = 1e1

	exp = Simulation(agentClass=minimalAgent)
	print("start simulation")
	exp.simulateEpisode()  # UntilTime(1)


# simulations.current.simulateTime(5)


# creates dictionary with (avg, std) for each x for each graph
# takes results as input, 
def assembleResults(resultsQueue, outputQueue, numResults=None, chooseBest=1.0):
	# process results into dict
	if numResults is None:
		numResults = resultsQueue.qsize()
	print("assembling results", numResults)
	graphs = dict()
	# print("")
	normaliseDict = dict()
	for i in range(numResults):
		result = resultsQueue.get()

		stdout.write("\rProgress: {:.2f}%".format((i + 1) / numResults * 100.0))
		stdout.flush()

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

		# print("adding", datapoint, "to", graphName, sample)
		graphs[graphName][sample].append(datapoint)

	# normalise if required
	# print()
	debug.out("normalise:", normaliseDict)
	# print("find max")
	# print("graphs", graphs)
	# for key in graphs:
	# 	print()
	# 	print(key)
	# 	print(graphs[key])

	# print()
	maxDict = dict()
	for name in graphs:
		if not normaliseDict[name]: continue

		graphDict = graphs[name]
		print("\n\n\n\nGraphDict:", name, graphDict)
		maxDict[name] = 0
		for sample in graphDict:
			# print(sample, graphDict[sample])
			maxDict[name] = np.max([maxDict[name], np.max(np.abs(graphDict[sample]))])
		# graphDict[sample] = np.array(graphDict[sample]) /

	# print('max', maxDict)
	for name in maxDict:
		maximum = maxDict[name]
		for sample in graphs[name]:
			graphs[name][sample] /= maximum

	# find the best graphs
	if chooseBest == 1.0:
		reducedGraph = graphs
	else:
		reducedGraph = dict()
		# populate full array so best can be chosen
		for key, graph in graphs.items():
			# print(f"choosing best {chooseBest} {chooseBest*len(graph[])}")
			# print("key", key)
			fullArray = []
			for x, ylist in graph.items():
				# print(x, len(ylist), ylist)
				fullArray.append(ylist)
			
			fullArray = np.array(fullArray)
			averages = np.average(fullArray, axis=0)
			# print('avg', averages)
			bestIndices = averages.argsort()[-int(chooseBest * fullArray.shape[1]):]
			print(fullArray.shape)
			print('best', bestIndices)

			# grab only the best results
			reducedGraph[key] = dict()
			for x, ylist in graph.items():
				reducedGraph[key][x] = np.array(ylist)[bestIndices].tolist()

			# print(fullArray)
			# print(fullArray.shape)

		print(f'\n\n\n{graphs}\n\n{reducedGraph}\n\n')



	# print("done with experiment")
	# calculate means and averages
	outputGraphs = dict()
	for key, graph in reducedGraph.items():
		# turn each list into a (value, error) tuple
		outputGraphs[key] = dict()
		for x, ylist in graph.items():
			# print()
			# print(ylist)
			confidence = 0.95
			n = len(ylist)
			m = scipy.mean(ylist)
			std_err = scipy.stats.sem(ylist)
			h = std_err * 1.96 / math.sqrt(n) # scipy.stats.t.ppf((1 + confidence) / 2, n - 1)

			outputGraphs[key][x] = (m, h)
			# print(ylist, key, x, outputGraphs[key][x], std_err) # , scipy.stats.t.ppf((1 + confidence) / 2, n - 1))
		# print(outputGraphs[key][x])
	# print ("processed")
	outputQueue.put(outputGraphs)


# creates dictionary with (avg, std) for each x for each graph
# takes results as input,
def assembleResultsBasic(resultsQueue, outputQueue, numResults=None):
	# process results into dict
	time.sleep(1)
	if numResults is None:
		numResults = resultsQueue.qsize()
	# print("assembling results", numResults)
	graphs = dict()
	# print("")
	for i in range(numResults):
		result = resultsQueue.get()
		# print('result', result)

		stdout.write("\rProgress: {:.2f}%".format((i + 1) / numResults * 100.0))
		stdout.flush()

		if len(result) == 4:
			graphName, sample, datapoint, normalise = result
		else:
			graphName, sample, datapoint = result
			normalise = False

		if graphName not in graphs.keys():
			graphs[graphName] = dict()

		if sample not in graphs[graphName].keys():
			graphs[graphName][sample] = list()
		# print ("creating list", graphName, sample)

		# print("adding", datapoint, "to", graphName, sample)
		graphs[graphName][sample].append(datapoint)


	# print('graphs', graphs)
	# calculate means and averages
	outputGraphs = dict()
	for key, graph in graphs.items():
		# turn each list into a (value, error) tuple
		outputGraphs[key] = dict()
		for x, ylist in graph.items():
			# print()
			# print(ylist)
			outputGraphs[key][x] = ylist
		# print(outputGraphs[key][x])
	# print ("processed")
	outputQueue.put(outputGraphs)
	# print(outputGraphs)


# print ("after")

# return outputGraphs

def executeMulti(processes, results, finished, numResults=None, assembly=assembleResults, chooseBest=1.0):
	if numResults is None:
		numResults = len(processes)

	print("Starting experiment:", len(processes), "@", constants.THREAD_COUNT)

	# results consumption thread:
	outputData = multiprocessing.Queue()
	assemble = multiprocessing.Process(target=assembly, args=(results, outputData, numResults, chooseBest,))
	assemble.start()

	# process simulation
	currentThreads = 0
	startedThreads = 0
	finishedThreads = 0
	while startedThreads < len(processes):
		while currentThreads < np.min([constants.THREAD_COUNT, len(processes)]):
			processes[startedThreads].start()
			startedThreads += 1
			currentThreads += 1
		# print('started', startedThreads)
		# print('current', currentThreads)

		# wait for at least one to finish
		finished.get()
		# print("got result")
		# processes[finishedThreads].join() #  is not None:	# print ('one down...')
		finishedThreads += 1
		currentThreads -= 1

	print("waiting for assemble...")
	# assemble.join()

	return outputData.get()


def doLocalJob(experiment, device):
	debug.out("LOCAL JOB", 'g')
	localJob = job(device, 5, hardwareAccelerated=True)
	decision = offloadingDecision.possibleActions[-1]
	print("decision is", decision)
	decision.updateDevice(device)
	localJob.setDecisionTarget(decision)
	experiment.addJob(device, localJob)
	experiment.simulateUntilJobDone()
	print("local done")


def doWaitJob(experiment, device):
	# fix decision to wait
	debug.out("\nWAIT JOB", 'g')
	waitJob = job(device, 5, hardwareAccelerated=True)
	decision = offloading.offloadingDecision.possibleActions[-2]
	decision.updateDevice(device)
	print("target index", decision.targetDeviceIndex)
	waitJob.setDecisionTarget(decision)
	experiment.addJob(device, waitJob)
	experiment.simulateTime(constants.PLOT_TD * 100)
	print("wait done")
	print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)


def doOffloadJob(experiment, source, destination):
	debug.out("OFFLOAD JOB", 'g')
	offloadJob = job(source, 5, hardwareAccelerated=True)
	decision = experiment.sharedAgent.possibleActions[destination.index]
	decision.updateDevice()
	print("target index", decision.targetDeviceIndex)
	offloadJob.setDecisionTarget(decision)
	experiment.addJob(source, offloadJob)
	print("offload 1 0")
	while destination.currentJob is not offloadJob:
		experiment.simulateTick()
		print('\n\n-\n')
	print("destination has job again")
	print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)
	decision = offloading.offloadingDecision.possibleActions[-2]
	decision.updateDevice(destination)
	offloadJob.setDecisionTarget(decision)
	# batch 2

	# time.sleep(1)
	print("\n\nshould activate now...")
	experiment.simulateTick()

	while destination.currentJob is not None or source.currentJob is not None:
		experiment.simulateTick()
		print('\n\n-\n')

	# assert offloadJob.immediate is False
	assert destination.currentJob is None

def setupMultithreading():
	import os
	os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

	print(multiprocessing.get_start_method(allow_none=False))
	multiprocessing.freeze_support()
	if multiprocessing.get_start_method(allow_none=False) != 'spawn':
		print("SETTING CONTEXT")
		multiprocessing.set_start_method('spawn', force=True)

# time.sleep(1)
# batch 1

if __name__ == '__main__':
	pass
	# for i in range(1, 100, 10):
	# 	print i, exp.simulateAll(i, "latency")

	# constants.DRAW_DEVICES = True
	# testPerformance()

	# singleDelayedJobLocal(False)
	# singleDelayedJobLocal(True)
	# doubleDelayedJobLocal(True)
	# differentBatchesLocal(True)
	# singleDelayedJobPeer(False)
	# singleDelayedJobPeer(True)
	# singleBatchLocal(True)
	# singleBatchLocal(False)
	# singleBatchRemote(False)
	# singleBatchRemote(True)
	# randomPeerJobs(True)
	# randomLocalJobs(False)
	# randomPeerJobs(False)
	# testActions()

	randomJobs(offloadingPolicy=REINFORCEMENT_LEARNING, hw=True)
# testPerformance()
# profileTarget()

# totalEnergyJobSize()
# testRepeatsSeparate()
# totalEnergyJobSize()
# totalEnergyBatchSize()
