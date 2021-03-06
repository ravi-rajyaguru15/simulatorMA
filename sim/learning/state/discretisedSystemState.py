import traceback
from copy import deepcopy

import numpy as np

from sim import debug
from sim.learning.state.systemState import systemState
from sim.simulations import constants


class discretisedSystemState(systemState):
	singlesDiscrete, multiplesDiscrete = None, None
	singlesScale, multiplesScale,  = None, None
	singlesScalingFactor, multiplesScalingFactor = None, None
	uniqueStates = None
	indexes = None

	multipliers = None

	def __init__(self, numDevices, singlesFields, singlesDiscrete, singlesScale, singlesScalingFactor, multiplesFields, multiplesDiscrete, multiplesScale, multiplesScalingFactor):
		# separate the names and options for fields
		self.singlesDiscrete = singlesDiscrete
		self.singlesScale = singlesScale
		self.singlesScalingFactor = singlesScalingFactor

		self.multiplesDiscrete = multiplesDiscrete
		self.multiplesScale = multiplesScale
		self.multiplesScalingFactor = multiplesScalingFactor

		# print("multipliers", self.multipliers)

		# # compute all indexes
		# computeIndeces()

		systemState.__init__(self, numDevices=numDevices, singles=singlesFields, multiples=multiplesFields)
		self.populateRestMultipliers()

	@staticmethod
	def convertTuples(numDevices, singlesWithDiscreteNum, multiplesWithDiscreteNum):
		# separate the names and options for fields
		singlesFields = []
		singlesDiscrete = dict()
		singlesScale = dict()
		singlesScalingFactor = dict()
		for value in singlesWithDiscreteNum:
			assert isinstance(value, discreteState)
			fieldName = value.name
			singlesFields.append(fieldName)
			singlesDiscrete[fieldName] = value.discreteOptions
			singlesScale[fieldName] = value.scale
			singlesScalingFactor[fieldName] = value.scalingFactor
		multiplesFields = []
		multiplesDiscrete = dict()
		multiplesScale = dict()
		multiplesScalingFactor = dict()
		for value in multiplesWithDiscreteNum:
			assert isinstance(value, discreteState)
			fieldName = value.name
			multiplesFields.append(fieldName)
			multiplesDiscrete[fieldName] = value.discreteOptions
			multiplesScale[fieldName] = value.scale
			multiplesScalingFactor[fieldName] = value.scalingFactor

		# print("convert tuple", numDevices)
		# print("init", singlesDiscrete)

		return numDevices, singlesFields, singlesDiscrete, singlesScale, singlesScalingFactor, multiplesFields, multiplesDiscrete, multiplesScale, multiplesScalingFactor
		# # compute all indexes
		# computeIndeces()

	def fromTuples(self, numDevices, singlesWithDiscreteNum, multiplesWithDiscreteNum):
		args = discretisedSystemState.convertTuples(numDevices, singlesWithDiscreteNum, multiplesWithDiscreteNum)
		return discretisedSystemState(*args)

	# def discretise(self):
	# 	for i in range(len(self.currentState)):
	# 		self.currentState[i] = discretisedSystemState.binariseValue(self.currentState[i])

	def expandField(self, field):
		assert field in self.singles or field in self.multiples
		if field in self.singles:
			self.singlesDiscrete[field] += 1
			if self.singlesScale[field]:
				self.singlesScalingFactor[field] += 1
			self.uniqueStates = None # ensure this gets recalculated
			self.populateRestMultipliers()
		else:
			raise Exception("not implemented")

	@staticmethod
	def discretiseValue(value, bins, scalingFactor, scale, field=None):
		# print("scale", value, bins, scalingFactor, scale)
		# capture boolean values
		if isinstance(value, bool):
			value = 1 if value else 0
		if scale:
			# assert value <= 1
			if value >= 1:
				# print("too big!", field, value, bins, scalingFactor, scale)
				return bins - 1
			else:
				return value * (scalingFactor)
				# return round(value * (scalingFactor - 1)) # do not round, because graceful failure doesn't
		else:
			assert value < bins
			return value

	# overrideScaling used to manually setup state based on index
	def setField(self, field, value, overrideScaling=False):
		assert field in self.dictRepresentation
		assert value >= 0
		assert value is not None

		# print("before", self.dictRepresentation)
		# debug.out("set %s to %s: %s" % (field, value, self.dictRepresentation[field][:]))
		if isinstance(value, list):
			for i in range(len(value)):
				if overrideScaling:
					self.dictRepresentation[field][i] = value[i]
				else:
					self.dictRepresentation[field][i] = discretisedSystemState.discretiseValue(value[i], self.multiplesDiscrete[field], self.multiplesScalingFactor[field], self.multiplesScale[field], field=field)
		else:
			if overrideScaling:
				self.dictRepresentation[field][:] = value
			else:
				self.dictRepresentation[field][:] = discretisedSystemState.discretiseValue(value, self.singlesDiscrete[field], self.singlesScalingFactor[field], self.singlesScale[field], field=field)
			# if field == self.energyField:
			# 	print("energy:", self.dictRepresentation[field][:], value, self.singlesDiscrete[field], self.singlesScalingFactor[field], self.singlesScale[field])

		# print("after", self.dictRepresentation)
		# print("set", field, value, self.dictRepresentation[field][:])
		# debug.out("set %s to %s: %s" % (field, value, self.dictRepresentation[field][:]))

	def getUniqueStates(self):
		if self.uniqueStates is None:
			self.uniqueStates = 1
			for single in self.singlesDiscrete:
				self.uniqueStates *= self.singlesDiscrete[single]
			for multiple in self.multiplesDiscrete:
				self.uniqueStates *= self.multiplesDiscrete[multiple] ** self.numDevices
		return self.uniqueStates

	def __addIndex(self, currentIndex, field, multiple):
		value = self.dictRepresentation[field]
		if multiple:
			width = self.multiplesDiscrete[field]
		else:
			width = self.singlesDiscrete[field]
		print("adding", field, value, width, currentIndex)
		return (currentIndex << width) + value

	# convert currentState to an integer index
	def getIndex(self, state=None):
		if state is None:
			state = self.currentState
		# debug.out("getting index: %s %s" % (self.currentState, self.multipliers))
		# debug.out("%s" % self.dictRepresentation)
		# print(state, self.multipliers, np.dot(state, self.multipliers))
		if None in state:
			return None
		else:
			return np.dot(state, self.multipliers)
		# return discretisedSystemState._getIndex(self.singlesDiscrete, self.singles, self.multiplesDiscrete, self.multiples, self.dictRepresentation)

	energyField = 'energyRemaining'
	def getGracefulFailureLevel(self):
		if self.energyField in self.singles:
			return 1. / self.singlesDiscrete[self.energyField]
		else:
			raise Exception("energyField not found")
			return systemState.getGracefulFailureLevel(self)

	def getStateDescription(self, index=None, enabled=True):
		if enabled:
			if index is None:
				return None # index = self.getIndex()
			elif isinstance(index, np.ndarray):
				index = self.getIndex(index)
			# print("index", index)

			description = ""
			for i in range(len(self.singles)):
				# calculate multiplication factor based on remaining states' options
				restMultiplier = 1
				if i < len(self.singles) - 1:
					for j in range(i + 1, len(self.singles)):
						restMultiplier *= self.singlesDiscrete[self.singles[j]]

				# field is value of this field in the singles set
				field = int(index / restMultiplier)
				if index >= restMultiplier:
					index -= restMultiplier * field
				description += "{} ={:2d} ".format(self.singles[i], field)
					# print(index)
			return description
		else:
			return "Not enabled"

	# create a clone form the index
	def fromIndex(self, index):
		duplicate = deepcopy(self)
		duplicate.createDictionaryRepresentation()
		# duplicate.currentState[0] = 5
		# print("duplicate:", duplicate.dictRepresentation, duplicate.currentState)

		for i in range(len(duplicate.singles)):
			restMultiplier = discretisedSystemState.getRestMultiplier(duplicate.singles, duplicate.singlesDiscrete, i)

			# field is value of this field in the singles set
			field = int(float(index) / restMultiplier)
			# print(restMultiplier, field, index)
			# last index
			if index >= restMultiplier: #  restMultiplier > 1 and
				index -= restMultiplier * field
			# description += "{} ={:2d} ".format(self.singles[i], field)
			duplicate.setField(duplicate.singles[i], field, overrideScaling=True)
				# print(index)
		return duplicate

	# create mapping for each index in old state to new state
	@staticmethod
	def convertIndexMap(originalState, expandedState):
		mapping = np.zeros((originalState.getUniqueStates(),), dtype=np.int)

		mapping = discretisedSystemState._recursiveIndexMap(mapping, originalState, expandedState, 0, values=np.zeros((len(originalState.singles),), dtype=np.int))

		return mapping

	@staticmethod
	def _recursiveIndexMap(mapping, originalState, expandedState, fieldIndex, values):

		if fieldIndex == len(originalState.singles) - 1:
			for i in range(originalState.singlesDiscrete[originalState.singles[fieldIndex]]):
				# continue
				mapping[np.dot(values, originalState.multipliers)] = np.dot(values, expandedState.multipliers)
				values[fieldIndex] += 1
		else:
			# recursively step through this field's discrete options
			for i in range(originalState.singlesDiscrete[originalState.singles[fieldIndex]]):
				discretisedSystemState._recursiveIndexMap(mapping, originalState, expandedState, fieldIndex + 1, values)
				values[fieldIndex] += 1
				values[fieldIndex + 1] = 0

		return mapping

	def populateRestMultipliers(self):
		self.multipliers = [discretisedSystemState.getRestMultiplier(self.singles, self.singlesDiscrete, i) for i in range(len(self.singles))]

	@staticmethod
	def getRestMultiplier(singles, singlesDiscrete, index):
		# calculate multiplication factor based on remaining states' options
		restMultiplier = 1
		if index < len(singles) - 1:
			for j in range(index + 1, len(singles)):
				restMultiplier *= singlesDiscrete[singles[j]]
		return restMultiplier

	def setState(self, arrayState):
		self.currentState = np.array(arrayState, dtype=np.dtype('b'))
		self.createDictionaryRepresentation()

class discreteState:
	name = None
	discreteOptions = None
	scale = None
	scalingFactor = None # used to add state for "full" e.g. jobQueue length

	def __init__(self, name, discreteOptions, scalingFactor=None, scale=True):
		self.name = name
		self.discreteOptions = discreteOptions
		self.scale = scale
		if scalingFactor is None:
			self.scalingFactor = self.discreteOptions
		else:
			self.scalingFactor = scalingFactor
