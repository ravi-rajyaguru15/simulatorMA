import multiprocessing

import numpy as np

import sim
from sim import debug
from sim.clock import clock
from sim.devices.elasticNode import elasticNode
from sim.learning import offloadingDecision, systemState
from sim.learning.agent.dqnAgent import dqnAgent as Agent
from sim.offloading import offloadingPolicy
from sim.simulations import constants, results
from sim.simulations.history import history
from sim.tasks.job import job
# from message import message
from sim.visualiser import visualiser

queueLengths = list()
currentSimulation = None

class BasicSimulation:
	currentSystemState = None
	finishedJobsList = []
	unfinishedJobsList = []
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
	completedJobs = None

	def __init__(self, hardwareAccelerated=None): # numEndDevices, numElasticNodes, numServers,
		# debug.out(numEndDevices + numElasticNodes)
		self.results = multiprocessing.Manager().Queue()
		# self.jobResults = multiprocessing.Manager().Queue()
		job.jobResultsQueue = multiprocessing.Manager().Queue()
		self.delays = list()
		self.completedJobs = 0

		self.time = clock()
		offloadingDecision.sharedClock = self.time
		
		# requires simulation to be populated
		self.currentSystemState = systemState.systemState(self)
		useSharedAgent = (constants.OFFLOADING_POLICY == offloadingPolicy.REINFORCEMENT_LEARNING) and (constants.CENTRALISED_LEARNING)

		results.learningHistory = history()

		print("Learning: shared: %s offloading: %s centralised: %s" % (useSharedAgent, constants.OFFLOADING_POLICY, constants.CENTRALISED_LEARNING))
		self.devices = [elasticNode(self.time, constants.DEFAULT_ELASTIC_NODE, self.results, i, episodeFinished=self.isEpisodeFinished, currentSystemState=self.currentSystemState, alwaysHardwareAccelerate=hardwareAccelerated) for i in range(constants.NUM_DEVICES)]

		if useSharedAgent:
			# create shared learning agent
			offloadingDecision.sharedAgent = Agent(self.currentSystemState)

		# self.ed = [] # endDevice(None, self, self.results, i, alwaysHardwareAccelerate=hardwareAccelerated) for i in range(numEndDevices)]
		# self.ed = endDevice()
		# self.ed2 = endDevice()
		if constants.OFFLOADING_POLICY == offloadingPolicy.REINFORCEMENT_LEARNING:
			if useSharedAgent:
				offloadingDecision.sharedAgent.setDevices(self.devices)
			else:
				for device in self.devices: device.decision.privateAgent.setDevices(self.devices)

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
		self.plotFrames = constants.PLOT_SKIP
		debug.out (self.plotFrames)
			
		# set all device options correctly
		# needs simulation and system state to be populated
		for device in self.devices: 
			# choose options based on policy
			device.setOffloadingDecisions(self.devices)

		sim.simulations.Simulation.currentSimulation = self
		
	def stop(self):
		debug.out("STOP", 'r')
		self.finished = True

		# dump incomplete jobs to job list
		for dev in self.devices:
			if dev.currentJob is not None:
				self.unfinishedJobsList.append(dev.currentJob)
			for batch in dev.batch:
				for job in dev.batch[batch]:
					self.unfinishedJobsList.append(job)

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
		offloadingDecision.sharedAgent.reset()

		# reset energy
		for dev in self.devices:
			dev.reset()

		self.time.reset()
		self.finished = False

	def isEpisodeFinished(self):
		return self.finished

	def getCompletedJobs(self): return self.completedJobs
	def incrementCompletedJobs(self, job):
		self.completedJobs += 1
		assert job not in self.finishedJobsList
		self.finishedJobsList.append(job)

	def getLatestFinishedJob(self):
		assert len(self.finishedJobsList) > 0
		return self.finishedJobsList[-1]

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
			debug.out("averages:")
			# debug.out ("latency:\t", 	np.average(np.array(latencies)))
			# debug.out ("energy:\t\t", 	np.average(np.array(energies)))
			# debug.out ("jobs:\t\t", 		np.average(queueLengths))
			debug.out (np.histogram(queueLengths, bins=np.array(range(np.max(queueLengths) + 3)) - .5))
		except:
			debug.out ("no results available")		



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
		for i in range(constants.NUM_DEVICES):
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

		newJob = job(device, constants.SAMPLE_SIZE.gen(), hardwareAccelerated=hardwareAccelerated, taskGraph=taskGraph)
		self.addJob(device, newJob)
		debug.out('creating %s on %s' % (newJob, device), 'r')
		debug.out("added job to device queue", 'p')

	# add job to device queue
	def addJob(self, device, job):
		device.numJobs += 1
		device.addJobToQueue(job)
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
