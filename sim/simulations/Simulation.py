import multiprocessing

import numpy as np

import sim
from sim import debug
from sim.clock import clock
from sim.devices.elasticNode import elasticNode
from sim.simulations import constants
from sim.tasks.job import job
from sim.visualiser import visualiser
from sim.learning.agent.agent import agent

queueLengths = list()
# currentSimulation = None

class BasicSimulation:
	sharedAgent = None

	episodeNumber = None
	currentSystemState = None
	# finishedJobsList = None
	latestFinishedJob = None
	numFinishedJobs = None
	totalFinishedJobsLifetime = None
	finishedTasks = None
	unfinishedJobsList = None
	ed, ed2, en, gw, srv, selectedOptions = None, None, None, None, None, None
	results = None
	jobResults = None
	time = None
	devices = None
	tasks = None
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
	useSharedAgent = None
	allowExpansion = None
	maxJobs = None
	offPolicy = None
	jobCounter = None

	def __init__(self, numDevices, maxJobs, numEnergyLevels, systemStateClass, reconsiderBatches, agentClass, tasks, globalClock=True,  allowExpansion=constants.ALLOW_EXPANSION, offPolicy=constants.OFF_POLICY, centralisedLearning=constants.CENTRALISED_LEARNING, trainClassification=True):
		hardwareAccelerated = True
		self.episodeNumber = 0
		self.allowExpansion = allowExpansion
		self.maxJobs = maxJobs
		self.offPolicy = offPolicy

		# debug.out(numEndDevices + numElasticNodes)
		self.results = multiprocessing.Manager().Queue()
		# self.jobResults = multiprocessing.Manager().Queue()
		# job.jobResultsQueue = multiprocessing.Manager().Queue()
		# self.delays = list()
		self.completedJobs = 0

		if globalClock:
			self.time = clock()
			agentClass.sharedClock = self.time

		self.tasks = tasks

		# requires simulation to be populated
		self.useSharedAgent = centralisedLearning
		# TODO: trainClassification in distributed 
		if self.useSharedAgent:
			self.currentSystemState = systemStateClass(numDevices=numDevices, maxJobs=maxJobs, numTasks=len(tasks), numEnergyLevels=numEnergyLevels)
			# create shared learning agent
			debug.out("creating shared agent %s" % agentClass)
			self.sharedAgent = agentClass(systemState=self.currentSystemState, reconsiderBatches=reconsiderBatches, owner=None, offPolicy=offPolicy, trainClassification=trainClassification)
			# TODO: need private state for non shared agent
			if debug.settings.enabled: print(self.sharedAgent)
			agentClass = self.sharedAgent


		# simulationResults.learningHistory = history()

		debug.out("Learning: shared: %s agent: %s centralised: %s" % (self.useSharedAgent, agentClass, centralisedLearning), 'r')
		self.devices = []
		for i in range(numDevices):
			self.addDevice(elasticNode(self.time, constants.DEFAULT_ELASTIC_NODE, self.results, i, maxJobs=maxJobs, reconsiderBatches=reconsiderBatches, currentSystemState=systemStateClass(numDevices=numDevices, maxJobs=maxJobs, numTasks=len(tasks), numEnergyLevels=numEnergyLevels), agent=agentClass, alwaysHardwareAccelerate=hardwareAccelerated, offPolicy=offPolicy, trainClassification=trainClassification))


			# offloadingDecision.offloadingDecision.createSharedAgent(self.currentSystemState, agentClass)
		# @staticmethod
		# def createSharedAgent(state, agentClass):
		# 	offloadingDecision.sharedAgent = agentClass(state)

		# self.ed = [] # endDevice(None, self, self.results, i, alwaysHardwareAccelerate=hardwareAccelerated) for i in range(numEndDevices)]
		# self.ed = endDevice()
		# self.ed2 = endDevice()
		# if constants.OFFLOADING_POLICY == offloadingPolicy.REINFORCEMENT_LEARNING:
		if self.useSharedAgent:
			# print("shared exists")
			assert self.sharedAgent is not None
			self.sharedAgent.setDevices(self.devices)
			self.sharedAgent.createModel()
		else:
			for device in self.devices: device.agent.setDevices(self.devices)
		# set offloading devices
		for device in self.devices: 
			device.setOffloadingOptions(self.devices)
			device.agent.createModel()

		# assemble expected lifetime for faster computation later
		self.populateDevicesExpectedLifetimes()

		# # self.en = elasticNode()
		# self.gw = [] #gateway()
		# self.srv = [] # [server() for i in range(numServers)]

		# self.devices = self.ed + self.en + self.srv
		self.taskQueueLength = [0] * len(self.devices)

		self.hardwareAccelerated = hardwareAccelerated
		debug.out("saving hardware acceleration as %s" % self.hardwareAccelerated)
		self.visualiser = visualiser(self)
		self.frames = 0
		self.plotFrames = constants.PLOT_SKIP
		debug.out(self.plotFrames)
			
		# set all device options correctly
		# needs simulation and system state to be populated
		# for device in self.devices:
		# 	# choose options based on policy
		# 	debug.out("setting shared: %s" % self.sharedAgent)
		# 	device.setOffloadingOptions(self.devices, )

		# sim.simulations.Simulation.currentSimulation = self

	def populateDevicesExpectedLifetimes(self):
		self.devicesExpectedLifetimeFunctions = [dev.expectedLifetime for dev in self.devices]
		self.devicesExpectedLifetimes = np.zeros((len(self.devices),))

	def getNumDevices(self): return len(self.devices)

	def addDevice(self, newDevice):
		self.devices.append(newDevice)
		self.populateDevicesExpectedLifetimes()

	def removeDevice(self):
		target = self.devices[0]

		self.devices.remove(target)

		for dev in self.devices:
			dev.removeDefaultOffloadingOption(target)

		self.populateDevicesExpectedLifetimes()

	def setFpgaIdleSleep(self, idleTime):
		for device in self.devices:
			if isinstance(device, elasticNode):
				device.fpga.idleTimeout = idleTime

	def setBatterySize(self, batterySize):
		for dev in self.devices:
			dev.setMaxEnergyLevel(batterySize)

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

	def simulateEpisodes(self, numEpisodes):
		for i in range(numEpisodes):
			self.simulateEpisode(i)

	# reset energy levels of all devices and run entire simulation
	def simulateEpisode(self, episodeNumber):
		self.reset(episodeNumber)
		i = 0
		while not self.finished:
			i += 1
			self.simulateTick()
			debug.out(debug.formatDebug("%s", [dev.energyLevel for dev in self.devices]))
		self.episodeNumber += 1

		# update target model if required
		if self.offPolicy:
			if self.useSharedAgent:
				if not self.sharedAgent.productionMode:
					self.sharedAgent.updateModel()
			else:
				for dev in self.devices:
					if not dev.agent.productionMode:
						dev.agent.updateModel()

	def reset(self, episodeNumber):
		if self.useSharedAgent:
			self.sharedAgent.reset(episodeNumber)
		# self.finishedJobsList = []
		self.latestFinishedJob = None
		self.finishedTasks = dict()
		self.numFinishedJobs = 0
		self.totalFinishedJobsLifetime = 0
		self.unfinishedJobsList = []
		job.id = 0

		# reset energy
		for dev in self.devices:
			dev.reset(episodeNumber)
		# print([dev.getEnergyLevelPercentage() for dev in self.devices])

		# time is None when not using global clock
		if self.time is not None:
			self.time.reset()
		self.finished = False
		self.jobCounter = 0

	def isEpisodeFinished(self):
		return self.finished

	def getCompletedJobs(self): return self.completedJobs
	def incrementCompletedJobs(self, job):
		self.completedJobs += 1
		# assert job not in self.finishedJobsList
		# self.finishedJobsList.append(job)
		self.latestFinishedJob = job
		self.numFinishedJobs += 1
		if job.currentTask not in self.finishedTasks:
			self.finishedTasks[job.currentTask] = 0
		self.finishedTasks[job.currentTask] += 1

		if job.owner.currentTime is not None:
			self.totalFinishedJobsLifetime += job.owner.currentTime - job.createdTime
		else:
			self.totalFinishedJobsLifetime += self.time.current - job.createdTime

	def getLatestFinishedJob(self):
		# assert len(self.finishedJobsList) > 0
		# return self.finishedJobsList[-1]
		return self.latestFinishedJob

	def simulateUntilTime(self, finalTime):
		self.simulateTime(finalTime - self.getCurrentTime())

	def getCurrentTime(self):
		if self.time is None:
			time = np.max([dev.currentTime.current for dev in self.devices])
		else:
			time = self.time.current
		return time

	def simulateTime(self, duration):
		# progress = 0
		endTime = self.getCurrentTime() + duration
		
		if self.finished: return

		while self.getCurrentTime() < endTime and not self.finished:
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

	def stopIfEpisodeDone(self):
		if any(self.devicesLifetimes() <= 0):
			self.stop()
		return self.finished

	def systemLifetime(self, devicesExpectedLifetimes=None):
		if devicesExpectedLifetimes is None:
			devicesExpectedLifetimes = self.devicesLifetimes()

		return np.min(devicesExpectedLifetimes)
	
	def devicesLifetimes(self):
		for i in range(self.getNumDevices()):
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
	def createNewJob(self, device, hardwareAccelerated=None):
		# if not set to hardwareAccelerate, use default
		if hardwareAccelerated is None:
			hardwareAccelerated = self.hardwareAccelerated
		# if still None, unknown behaviour
		assert (hardwareAccelerated is not None)

		# print("create job", self.tasks)
		# select task for this job
		task = self.tasks
		if isinstance(self.tasks, list):
			if len(self.tasks) > 1:
				task = [np.random.choice(self.tasks)]
				# print("chose task", task)



		newJob = job(device, self.jobCounter, constants.SAMPLE_SIZE.gen(), isEpisodeFinished=self.isEpisodeFinished, incrementCompletedJobs=self.incrementCompletedJobs, hardwareAccelerated=hardwareAccelerated, taskGraph=task)
		self.jobCounter += 1
		# print(device.currentTime, device, "created", newJob)
		self.addJob(device, newJob)
		debug.out('creating %s on %s' % (newJob, device), 'r')
		debug.out("added job to device queue", 'p')

	# add job to device queue
	def addJob(self, device, job):
		device.numJobs += 1
		device.addJobToQueue(job)

	@staticmethod
	def timeOutSleep(processor):
		raise Exception("Not implemented in BasicSimulation")
