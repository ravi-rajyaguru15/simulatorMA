import numpy as np

import sim.debug
import sim.simulations.constants
from sim import debug
from sim.simulations import constants


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

	maxJobs = None
	numDevices = None
	genericException = None

	# singles are individual states, multiples are per device
	def __init__(self, numDevices, singles, multiples):
		self.genericException = Exception("not implemented in " + str(self.__class__.__name__))

		self.singles = singles
		self.multiples = multiples
		self.stateCount = numDevices * len(multiples) + len(singles)
		self.batchLengths = np.array([0] * numDevices)
		self.currentState = np.zeros((self.stateCount,))
		self.numDevices = numDevices

		assert self.stateCount == len(singles) + len(multiples) * numDevices

		self.setState(self.currentState)
		# self.dictRepresentation = systemState.createDictionaryRepresentation(self.currentState)

		# self.setSimulation(simulation)

	def setState(self, arrayState):
		assert arrayState is not None
		self.currentState = np.array(arrayState)
		self.createDictionaryRepresentation()

	def getCurrentState(self, task, job, device):
		self.updateState(task, job, device)
		return np.array(self.currentState)

	# @staticmethod
	def createDictionaryRepresentation(self):
		# self.dictRepresentation = systemState.createDictionaryRepresentation(self.currentState)
		self.dictRepresentation = self.getDictionaryRepresentation(self.currentState, self.singles, self.multiples)
		# print('i', i)
		# self.dictRepresentation['batchLengths']

	# @staticmethod
	def getDictionaryRepresentation(self, arrayRepresentation, singles, multiples):
		# link array elements to dictionary for easier access
		dictRepresentation = dict()
		# debug.out("creating dictionary representation from " + str(arrayRepresentation.shape))
		for i in range(len(singles)):
			dictRepresentation[singles[i]] = arrayRepresentation[i:i + 1]
		for i in range(len(multiples)):
			dictRepresentation[multiples[i]] = arrayRepresentation[(len(singles) + i * self.numDevices):(len(singles) + (i + 1) * sim.simulations.constants.NUM_DEVICES)]

		return dictRepresentation

	# @classmethod

	def __sub__(self, otherState):
		difference = self.currentState - otherState.currentState
		return self.getDictionaryRepresentation(difference, self.singles, self.multiples)

	# def setSimulation(self, simulation):
	# 	self.devicesLifetimesFunction = simulation.devicesLifetimes
	# 	self.systemExpectedLifeFunction = simulation.systemLifetime
	# 	self.taskBatchLengthsFunction = simulation.taskBatchLengths
	# 	self.currentTime = simulation.time

	def __repr__(self):
		return str(self.currentState)

	def updateState(self, device, job, task):
		raise self.genericException

	def getGracefulFailureLevel(self):
		return constants.GRACEFUL_FAILURE_LEVEL

	def setField(self, field, value):
		assert field in self.dictRepresentation
		# print("setting field {} to {}".format(field, value))
		self.dictRepresentation[field][:] = value

	def getField(self, field):
		assert field in self.dictRepresentation
		return self.dictRepresentation[field]