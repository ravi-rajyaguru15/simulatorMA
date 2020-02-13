import sim.simulations.constants
import sim.debug

import numpy as np

from sim import debug

class systemState:
	currentTask = None
	currentState = None
	
	currentTime = None # not added as input

	stateCount = None
	dictRepresentation = None

	devicesLifetimesFunction = None
	systemExpectedLifeFunction = None
	taskBatchLengthsFunction = None
	singles, multiples = None, None
	genericException = None


	# singles are individual states, multiples are per device
	def __init__(self, simulation, singles, multiples):
		self.genericException = Exception("not implemented in " + str(self.__class__.__name__))

		self.singles = singles
		self.multiples = multiples
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
		self.dictRepresentation = systemState.getDictionaryRepresentation(self.currentState, self.singles, self.multiples)
		# print('i', i)
		# self.dictRepresentation['batchLengths']

	@staticmethod
	def getDictionaryRepresentation(arrayRepresentation, singles, multiples):
		# link array elements to dictionary for easier access
		dictRepresentation = dict()
		debug.out("creating dictionary representation from " + str(arrayRepresentation.shape))
		# time.sleep(0.5)
		for i in range(len(singles)):
			dictRepresentation[singles[i]] = arrayRepresentation[i:i + 1]
		for i in range(len(multiples)):
			dictRepresentation[multiples[i]] = arrayRepresentation[(len(singles) + i * sim.simulations.constants.NUM_DEVICES):(len(singles) + (i + 1) * sim.simulations.constants.NUM_DEVICES)]

		return dictRepresentation

	# @classmethod
	def fromSystemState(self, simulation):
		second = self.__class__(simulation)

		second.setState(self.currentState)

		# second.dictRepresentation = systemState.createDictionaryRepresentation(second.currentState)
		return second

	def __sub__(self, otherState):
		difference = self.currentState - otherState.currentState
		return systemState.getDictionaryRepresentation(difference, self.singles, self.multiples)

	def setSimulation(self, simulation):
		self.devicesLifetimesFunction = simulation.devicesLifetimes
		self.systemExpectedLifeFunction = simulation.systemLifetime
		self.taskBatchLengthsFunction = simulation.taskBatchLengths
		self.currentTime = simulation.time

	def __repr__(self):
		return str(self.currentState)

	def updateState(self, device, job, task):
		raise self.genericException

	# def updateSystem(self):
	# 	raise self.genericException
	# def updateTask(self, task):
	# 	raise self.genericException
	# def updateJob(self, job):
	# 	raise self.genericException
	# def updateDevice(self, device):
	# 	raise self.genericException

	def setField(self, field, value):
		assert field in self.dictRepresentation
		# print("setting field {} to {}".format(field, value))
		self.dictRepresentation[field][:] = value

	def getField(self, field):
		assert field in self.dictRepresentation
		return self.dictRepresentation[field]