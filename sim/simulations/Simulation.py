import multiprocessing

import numpy as np

import sim.constants
import sim.debug
import sim.history
import sim.offloadingDecision
import sim.offloadingPolicy
import sim.results
import sim.systemState
import sim.tasks
import sim.variable
from sim.clock import clock
from sim.elasticNode import elasticNode
from sim.endDevice import endDevice
from sim.job import job
# from message import message
from sim.visualiser import visualiser

queueLengths = list()
current = None


class BasicSimulation:
	ed, ed2, en, gw, srv, selectedOptions = None, None, None, None, None, None
	results = None
	jobResults = None
	time = None
	devices = None
	devicesExpectedLifetimeFunctions = None
	devicesExpectedLifetimes = None
	numDevices = None
	delays = None
	currentDelays = None
	taskQueueLength = None
	# visualise = None
	visualisor = None
	frames = None
	plotFrames = None
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
		sim.systemState.current = sim.systemState.systemState(self)
		useSharedAgent = (sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.REINFORCEMENT_LEARNING) and (sim.constants.CENTRALISED_LEARNING)

		sim.results.learningHistory = sim.history.history()

		print(useSharedAgent, sim.constants.OFFLOADING_POLICY, sim.constants.CENTRALISED_LEARNING)
		if useSharedAgent:
			# create shared learning agent
			sim.offloadingDecision.sharedAgent = sim.offloadingDecision.agent(sim.systemState.current)
		
		# self.ed = [] # endDevice(None, self, self.results, i, alwaysHardwareAccelerate=hardwareAccelerated) for i in range(numEndDevices)]
		# self.ed = endDevice()
		# self.ed2 = endDevice()
		print("default", sim.constants.DEFAULT_ELASTIC_NODE, sim.constants.DEFAULT_ELASTIC_NODE.RECONFIGURATION_TIME, sim.constants.DEFAULT_ELASTIC_NODE.RECONFIGURATION_TIME.gen())
		self.devices = [elasticNode(self, sim.constants.DEFAULT_ELASTIC_NODE, self.results, i, episodeFinished=self.isEpisodeFinished, alwaysHardwareAccelerate=hardwareAccelerated) for i in range(sim.constants.NUM_DEVICES)]
		sim.offloadingDecision.devices = self.devices
		if useSharedAgent:
			sim.offloadingDecision.sharedAgent.setDevices()
		else:
			if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.REINFORCEMENT_LEARNING:
				for device in self.devices: device.decision.privateAgent.setDevices()
		# assemble expected lifetime for faster computation later
		self.devicesExpectedLifetimeFunctions = [dev.expectedLifetime for dev in self.devices]
		self.devicesExpectedLifetimes = np.zeros((len(self.devices),))
		# # self.en = elasticNode()
		# self.gw = [] #gateway()
		# self.srv = [] # [server() for i in range(numServers)]

		# self.devices = self.ed + self.en + self.srv
		self.taskQueueLength = [0] * len(self.devices)

		self.hardwareAccelerated = hardwareAccelerated
		self.visualiser = visualiser(self)
		self.frames = 0
		self.plotFrames = sim.constants.PLOT_TD / sim.constants.TD
		sim.debug.out (self.plotFrames)
			
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
		while not self.finished:
			self.simulateTick()
	
	# if multiple jobs finish in the same line, 
	def simulateUntilJobDone(self):
		numJobs = self.completedJobs
		while self.completedJobs == numJobs:
			self.simulateTick()

	def simulateTick(self):
		raise NotImplementedError("Implemented in subclass")

	# reset energy levels of all devices and run entire simulation
	def simulateEpisode(self):
		self.reset()
		while not self.finished:
			self.simulateTick()

	def reset(self):
		sim.offloadingDecision.sharedAgent.reset()

		# reset energy
		for dev in self.devices:
			dev.reset()

		self.time.reset()
		self.finished = False

	def isEpisodeFinished(self):
		return self.finished

	def getCompletedJobs(self): return self.completedJobs
	def incrementCompletedJobs(self): self.completedJobs += 1

	def simulateUntilTime(self, finalTime):
		assert(finalTime > self.time)
		self.simulateTime(finalTime - self.time)

	def simulateTime(self, duration):
		# progress = 0
		endTime = self.time + duration
		
		if self.finished: return

		while self.time < endTime and not self.finished:
			# try:
			if True:
				self.simulateTick()
		
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
			
			queueLengths = np.array(sim.simulations.Simulation.queueLengths)
			sim.debug.out("averages:")
			# sim.debug.out ("latency:\t", 	np.average(np.array(latencies)))
			# sim.debug.out ("energy:\t\t", 	np.average(np.array(energies)))
			# sim.debug.out ("jobs:\t\t", 		np.average(queueLengths))
			sim.debug.out (np.histogram(queueLengths, bins=np.array(range(np.max(queueLengths) + 3)) - .5))
		except:
			sim.debug.out ("no results available")		



	def taskBatchLengths(self, task):
		return [len(dev.batch[task]) if task in dev.batch else 0 for dev in self.devices]

	def batchLengths(self):
		return [dev.batchLengths() for dev in self.devices]
	
	def maxBatchLengths(self):
		return [np.max(lengths) if len(lengths) > 0 else 0 for lengths in self.batchLengths()]

	def devicesNames(self):
		return [dev for dev in self.devices]

	def totalDevicesEnergy(self):
		return [dev.totalEnergyCost for dev in self.devices]

	def currentDevicesEnergy(self):
		return [dev.energy() for dev in self.devices]

	def systemLifetime(self, devicesExpectedLifetimes=None):
		if devicesExpectedLifetimes is None:
			devicesExpectedLifetimes = self.devicesLifetimes()

		return np.min(devicesExpectedLifetimes)
	
	def devicesLifetimes(self):
		for i in range(sim.constants.NUM_DEVICES):
			self.devicesExpectedLifetimes[i] = self.devicesExpectedLifetimeFunctions[i]()
		return self.devicesExpectedLifetimes
			# return [dev.expectedLifetime() for dev in self.devices]

	def devicesEnergyLevels(self):
		return [dev.energyLevel for dev in self.devices]

	def numSelectedOptions(self):
		if self.selectedOptions is None:
			return self.numOptions()
		else:
			return len(self.selectedOptions)

	def selectedNameOptions(self):
		return [self.optionsNames[option] for option in self.selectedOptions]

	# create job and add to device
	def createNewJob(self, device, hardwareAccelerated=None, taskGraph=None):
		# if not set to hardwareAccelerate, use default
		if hardwareAccelerated is None:
			hardwareAccelerated = self.hardwareAccelerated
		# if still None, unknown behaviour
		assert (hardwareAccelerated is not None)

		sim.debug.out('creating job on %s' % device, 'r')
		newJob = job(device, sim.constants.SAMPLE_SIZE.gen(), hardwareAccelerated=hardwareAccelerated, taskGraph=taskGraph)
		self.addJob(device, newJob)
		print("created", newJob)
		sim.debug.out("added job to device queue", 'p')

	# add job to device queue
	def addJob(self, device, job):
		device.numJobs += 1
		device.jobQueue.append(job)
# if __name__ == '__main__':
# 	print ("running sim")

# 	# for i in range(1, 100, 10):
# 	# 	print i, simulation.simulateAll(i, "latency")

# 	# simulation.singleDelayedJobLocal(False)
# 	# simulation.singleDelayedJobLocal(True)
# 	# simulation.singleDelayedJobPeer(False)
# 	# simulation.singleDelayedJobPeer(True)
# 	# simulation.randomPeerJobs(True)
# 	simulation.randomPeerJobs(False)
# 	# simulation.singleBatchLocal(False)
