import time
import traceback

import sim.simulations.constants
import sim.debug

import numpy as np

# used as shared variable
# current = None
singles = ['taskIdentifier', 'taskSize', 'selfDeviceIndex', 'selfExpectedLife', 'systemExpectedLife',
		   'deadlineRemaining', 'selfBatch', 'selfCurrentConfig']
multiples = ['expectedLife', 'batchLengths', 'allConfig']

class systemState:
	# simulation = None
	currentTask = None
	currentState = None
	
	# simulation states
	# batchLengths = [None]
	# expectedLife = None
	# self states
	# selfDeviceIndex = None
	# selfBatch = None
	# selfExpectedLife = None
	# selfCurrentConfiguration = None
	# task states
	# taskSize = None
	# taskIdentifier = None
	# deadlineRemaining = None
	currentTime = None # not added as input 
	# task size, data size, identifier, current config, deadline

	stateCount = None
	dictRepresentation = None

	devicesLifetimesFunction = None
	systemExpectedLifeFunction = None
	taskBatchLengthsFunction = None



	def __init__(self, simulation):
	# 	self.simulation = simulation
	# 	print("statecount", self.stateCount)
		self.stateCount = sim.simulations.constants.NUM_DEVICES * len(multiples) + len(singles)
		self.batchLengths = np.array([0] * sim.simulations.constants.NUM_DEVICES)
		self.currentState = np.zeros((self.stateCount,))

		assert self.stateCount == len(singles) + len(multiples) * sim.simulations.constants.NUM_DEVICES

		self.setState(self.currentState)
		# self.dictRepresentation = systemState.createDictionaryRepresentation(self.currentState)

		self.setSimulation(simulation)

	def setState(self, arrayState):
		self.currentState = np.array(arrayState)
		self.createDictionaryRepresentation()

	# @staticmethod
	def createDictionaryRepresentation(self):
		# self.dictRepresentation = systemState.createDictionaryRepresentation(self.currentState)
		self.dictRepresentation = systemState.getDictionaryRepresentation(self.currentState)
		# print('i', i)
		# self.dictRepresentation['batchLengths']

	@staticmethod
	def getDictionaryRepresentation(arrayRepresentation):
		# link array elements to dictionary for easier access
		dictRepresentation = dict()
		print("creating dictionary representation from " + str(arrayRepresentation.shape))
		time.sleep(0.5)
		for i in range(len(singles)):
			dictRepresentation[singles[i]] = arrayRepresentation[i:i + 1]
		for i in range(len(multiples)):
			dictRepresentation[multiples[i]] = arrayRepresentation[(len(singles) + i * sim.simulations.constants.NUM_DEVICES):(len(singles) + (i + 1) * sim.simulations.constants.NUM_DEVICES)]

		return dictRepresentation

	@classmethod
	def fromSystemState(cls, simulation):
		second = cls(simulation)

		second.setState(simulation.currentSystemState.currentState)

		# second.dictRepresentation = systemState.createDictionaryRepresentation(second.currentState)
		return second

	def __sub__(self, otherState):
		difference = self.currentState - otherState.currentState
		return systemState.getDictionaryRepresentation(difference)

	def setSimulation(self, simulation):
		self.devicesLifetimesFunction = simulation.devicesLifetimes
		self.systemExpectedLifeFunction = simulation.systemLifetime
		self.taskBatchLengthsFunction = simulation.taskBatchLengths
		self.currentTime = simulation.time

	def __repr__(self):
		return str(self.currentState)

	def updateSystem(self):
		# self.stateCount = simulation.constants.NUM_DEVICES * 2 + 7
		# self.simulation = simulation

		# self.expectedLife = self.devicesLifetimesFunction()
		# self.systemExpectedLife = self.systemExpectedLifeFunction()

		# sim.debug.out("update system: {} {}".format(self.expectedLife, self.currentTime))
		expectedLifetimes = self.devicesLifetimesFunction()
		self.setField('expectedLife', expectedLifetimes)
		self.setField('systemExpectedLife', self.systemExpectedLifeFunction(expectedLifetimes))
		# sim.debug.out(self.dictRepresentation)
		# self.update()

	# the order is important, therefore the other functions are private
	def update(self, task, job, device):
		sim.debug.learnOut("updating systemState with [{}] [{}] [{}]".format(task, job, device), 'c')
		self.__updateTask(task)
		self.__updateJob(job)
		self.__updateDevice(device)

		# sim.debug.learnOut(self.dictRepresentation)

	# update the system state based on which task is to be done
	def __updateTask(self, task):
		self.currentTask = task
		
		# self.batchLengths = self.taskBatchLengthsFunction(task)
		# self.taskIdentifier = task.identifier
		# self.taskSize = task.rawSize

		# sim.debug.out("update task {} {} {} {}".format(self.currentTask, self.batchLengths, self.taskIdentifier, self.taskSize))
		self.setField('batchLengths', self.taskBatchLengthsFunction(task))
		self.setField('taskIdentifier', task.identifier)
		self.setField('taskSize', task.rawSize)
	
		# sim.debug.out(self.dictRepresentation)

		# self.update()

	def __updateJob(self, job):
		# self.deadlineRemaining = np.max([0, job.deadlineTime - self.currentTime.current])
		# sim.debug.out('update job {}'.format(self.deadlineRemaining))
		remaining = job.deadlineTime - self.currentTime.current
		self.setField('deadlineRemaining', remaining if remaining >= 0 else 0)

		# sim.debug.out(self.dictRepresentation)
		# self.update()

	def __updateDevice(self, device):
		# self.selfBatch = len(device.batch[self.currentTask]) if self.currentTask is not None and self.currentTask in device.batch else 0
		# self.selfExpectedLife = device.expectedLifetime()
		# self.selfDeviceIndex = device.index

		# if device.hasFpga():
		# 	if device.fpga.currentConfig is not None:
		# 		self.selfCurrentConfiguration = device.fpga.currentConfig.identifier
		# 	else:
		# 		self.selfCurrentConfiguration = 0
		# else:
		# 	self.selfCurrentConfiguration = 0

		# print('update device', self.selfBatch, self.selfExpectedLife, self.selfDeviceIndex)
		self.setField('selfBatch', len(device.batch[self.currentTask]) if self.currentTask is not None and self.currentTask in device.batch else 0)
		self.setField('selfExpectedLife', device.expectedLifetime())
		self.setField('selfDeviceIndex', device.index)
		
		self.setField('selfCurrentConfig', device.getCurrentConfiguration())


		# sim.debug.out(self.dictRepresentation)

		# self.update()
		# sys.exit(0)

	def setField(self, field, value):
		assert field in self.dictRepresentation
		# print("setting field {} to {}".format(field, value))
		self.dictRepresentation[field][:] = value

	def getField(self, field):
		assert field in self.dictRepresentation
		return self.dictRepresentation[field]