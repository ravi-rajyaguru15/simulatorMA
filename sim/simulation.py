from sim.endDevice import endDevice
from sim.elasticNode import elasticNode
# from message import message
from sim.result import result
from sim.gateway import gateway
from sim.server import server
from sim.visualiser import visualiser 
from sim.job import job
from sim.clock import clock
import sim.systemState
import sim.offloadingDecision
import sim.offloadingPolicy
import sim.debug

import sim.constants
import sim.variable
import sim.tasks

import multiprocessing
import sys
import numpy as np
import warnings
import datetime

queueLengths = list()
current = None

class simulation:
	ed, ed2, en, gw, srv, selectedOptions = None, None, None, None, None, None
	results = None
	jobResults = None
	time = None
	devices = None
	numDevices = None
	delays = None
	currentDelays = None
	taskQueueLength = None
	# visualise = None
	visualisor = None
	finished = False
	hardwareAccelerated = None
	timestamps = list()
	lifetimes = list()
	energylevels = list()
	systemState = None
	completedJobs = None

	def __init__(self, hardwareAccelerated=None): # numEndDevices, numElasticNodes, numServers,
		# sim.debug.out(numEndDevices + numElasticNodes)
		self.results = multiprocessing.Manager().Queue()
		# self.jobResults = multiprocessing.Manager().Queue()
		job.jobResultsQueue = multiprocessing.Manager().Queue()
		self.delays = list()
		self.completedJobs = 0

		self.time = clock()
		sim.offloadingDecision.sharedClock = self.time
		
		# requires simulation to be populated
		sim.systemState.current = sim.systemState.systemState()
		useSharedAgent = sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.REINFORCEMENT_LEARNING and sim.constants.CENTRALISED_LEARNING
			
		if useSharedAgent:
			# create shared learning agent
			sim.offloadingDecision.sharedAgent = sim.offloadingDecision.agent(sim.systemState.current)
		
		# self.ed = [] # endDevice(None, self, self.results, i, alwaysHardwareAccelerate=hardwareAccelerated) for i in range(numEndDevices)]
		# self.ed = endDevice()
		# self.ed2 = endDevice()
		self.devices = [elasticNode(self, sim.constants.DEFAULT_ELASTIC_NODE, self.results, i, alwaysHardwareAccelerate=hardwareAccelerated) for i in range(sim.constants.NUM_DEVICES)]
		if useSharedAgent:
			sim.offloadingDecision.sharedAgent.setDevices(self.devices)
		
		# # self.en = elasticNode()
		# self.gw = [] #gateway()
		# self.srv = [] # [server() for i in range(numServers)]

		# self.devices = self.ed + self.en + self.srv
		self.taskQueueLength = [0] * len(self.devices)

		self.hardwareAccelerated = hardwareAccelerated
		self.visualiser = visualiser(self)


		# set all device options correctly
		# needs simulation and system state to be populated
		for device in self.devices: 
			# choose options based on policy
			device.setOffloadingDecisions(self.devices)

		
	def stop(self):
		sim.debug.out("STOP", 'r')
		self.finished = True

	def allDone(self):
		return np.all([not device.hasJob() for device in self.devices])
	
	def simulate(self):
		frames = 0
		plotFrames = sim.constants.PLOT_TD / sim.constants.TD

		while not self.finished:
			frames += 1
			self.simulateTick()
			
			# if sim.constants.DRAW_DEVICES:
			if frames % plotFrames == 0:
				self.visualiser.update()
		
			# pass
				# def simulateUntilDone()
	
	# if multiple jobs finish in the same line, 
	def simulateUntilJobDone(self):
		numJobs = self.completedJobs
		while self.completedJobs == numJobs:
			self.simulateTick()

	def getCompletedJobs(self): return self.completedJobs
	def incrementCompletedJobs(self): self.completedJobs += 1

	def simulateUntilTime(self, finalTime):
		assert(finalTime > self.time)
		self.simulateTime(finalTime - self.time)

	def simulateTime(self, duration):
		# progress = 0
		endTime = self.time + duration
		plotFrames = sim.constants.PLOT_TD / sim.constants.TD
		sim.debug.out (plotFrames)
		frames = 0

		while self.time < endTime and not self.finished:
			# try:
			if True:
				self.simulateTick()
				frames += 1

				# if sim.constants.DRAW_DEVICES:
				if frames % plotFrames == 0:
					self.visualiser.update()
		
		# results
		try:
			latencies = list()
			energies = list()
			for i in range(self.results.qsize()):
				value = self.results.get()
				
				samples = value[0]
				res = value[1]
	
				latencies.append(res.latency)
				energies.append(res.energy)
			
			queueLengths = np.array(queueLengths)
			sim.debug.out("averages:")
			# sim.debug.out ("latency:\t", 	np.average(np.array(latencies)))
			# sim.debug.out ("energy:\t\t", 	np.average(np.array(energies)))
			# sim.debug.out ("jobs:\t\t", 		np.average(queueLengths))
			sim.debug.out (np.histogram(queueLengths, bins=np.array(range(np.max(queueLengths) + 3)) - .5))
		except:
			sim.debug.out ("no results available")		


	def simulateTick(self):
		# try:
		if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.REINFORCEMENT_LEARNING:

			sim.systemState.current.updateSystem(self)
		# create new jobs
		for device in self.devices:
			# mcu is required for taking samples
			if not device.hasJob():
				device.maybeAddNewJob()

		# update the destination of the offloading if it is shared
		if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.ROUND_ROBIN:
			sim.offloadingDecision.updateOffloadingTarget()
		
		tasksBefore = np.array([dev.currentSubtask for dev in self.devices])

		# update all the devices
		for dev in self.devices:
			dev.updateTime(self.time)
			queueLengths.append(len(dev.jobQueue))

		# capture energy values
		for dev in self.devices:
			energy = dev.energy()

			# # add energy to device counter
			# dev.totalEnergyCost += energy
			# add energy to job 
			if dev.currentJob is not None:
				dev.currentJob.totalEnergyCost += energy
				# see if device is in job history
				if dev not in dev.currentJob.devicesEnergyCost.keys():
					dev.currentJob.devicesEnergyCost[dev] = 0
				
				dev.currentJob.devicesEnergyCost[dev] += energy
		if sim.constants.DRAW_GRAPH_EXPECTED_LIFETIME:
			# note energy levels for plotting
			self.timestamps.append(self.time)
			self.lifetimes.append(self.devicesLifetimes())
			self.energylevels.append(self.devicesEnergyLevels())
			

		# check if task queue is too long
		self.taskQueueLength = [len(dev.taskQueue) for dev in self.devices]
		# for i in range(len(self.devices)):
		# 	if self.taskQueueLength[i] > sim.constants.MAXIMUM_TASK_QUEUE:
		# 		# check distribution of job assignments
		# 		unique, counts = np.unique(np.array(sim.results.chosenDestinations[:-1]), return_counts=True)
		# 		print(dict(zip(unique, counts)))

		# 		warnings.warn("TaskQueue for {} too long! {} Likelihood: {}".format(self.devices[i], len(self.devices[i].taskQueue), sim.constants.JOB_LIKELIHOOD))
			


		self.currentDelays = [dev.currentSubtask.delay if dev.currentSubtask is not None else 0 for dev in self.devices ]
		self.delays.append(self.currentDelays)

		# print all results if interesting
		tasksAfter = np.array([dev.currentSubtask for dev in self.devices])
		if sim.debug.enabled:
			if not (np.all(tasksAfter == None) and np.all(tasksBefore == None)):
				sim.debug.out('tick {}'.format(self.time), 'b')
			# 	sim.debug.out("nothing...")
			# else:
				sim.debug.out("tasks before {0}".format(tasksBefore), 'r')
				sim.debug.out("have jobs:\t{0}".format([dev.hasJob() for dev in self.devices]), 'b')
				sim.debug.out("jobQueues:\t{0}".format([len(dev.jobQueue) for dev in self.devices]), 'g')
				sim.debug.out("batchLengths:\t{0}".format(self.batchLengths()), 'c')
				sim.debug.out("currentBatch:\t{0}".format([dev.currentBatch for dev in self.devices]))
				sim.debug.out("currentConfig:\t{0}".format([dev.fpga.currentConfig for dev in self.devices if isinstance(dev, elasticNode)]))
				sim.debug.out("taskQueues:\t{0}".format([len(dev.taskQueue) for dev in self.devices]), 'dg')
				sim.debug.out("taskQueues:\t{0}".format([[task for task in dev.taskQueue] for dev in self.devices]), 'dg')
				sim.debug.out("states: {0}".format([[comp.state for comp in dev.components] for dev in self.devices]))
				sim.debug.out("tasks after {0}".format(tasksAfter), 'r')
			
				if np.sum(self.currentDelays) > 0:
					sim.debug.out("delays {}".format(self.currentDelays))

		# progress += sim.constants.TD
		self.time.increment()

	def taskBatchLengths(self, task):
		return [len(dev.batch[task]) if task in dev.batch else 0 for dev in self.devices]

	def batchLengths(self):
		return [[len(batch) for key, batch in dev.batch.items()] for dev in self.devices]
	
	def maxBatchLengths(self):
		return [np.max(lengths) if len(lengths) > 0 else 0 for lengths in self.batchLengths()]

	def devicesNames(self):
		return [dev for dev in self.devices]

	def totalDevicesEnergy(self):
		return [dev.totalEnergyCost for dev in self.devices]

	def currentDevicesEnergy(self):
		return [dev.energy() for dev in self.devices]

	def systemLifetime(self):
		return np.min(self.devicesLifetimes())
		
	def devicesLifetimes(self):
		return [dev.expectedLifetime() for dev in self.devices]

	def devicesEnergyLevels(self):
		return [dev.energyLevel for dev in self.devices]

	def numSelectedOptions(self):
		if self.selectedOptions is None:
			return self.numOptions()
		else:
			return len(self.selectedOptions)

	def selectedNameOptions(self):
		return [self.optionsNames[option] for option in self.selectedOptions]
	

if __name__ == '__main__':
	print ("running sim")

	# for i in range(1, 100, 10):
	# 	print i, simulation.simulateAll(i, "latency")

	# simulation.singleDelayedJobLocal(False)
	# simulation.singleDelayedJobLocal(True)
	# simulation.singleDelayedJobPeer(False)
	# simulation.singleDelayedJobPeer(True)
	# simulation.randomPeerJobs(True)
	simulation.randomPeerJobs(False)
	# simulation.singleBatchLocal(False)
