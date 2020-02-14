import numpy as np

from sim import debug
from sim.learning.state.systemState import systemState
from sim.simulations import constants


class discretisedSystemState(systemState):
	singlesDiscrete, multiplesDiscrete = None, None
	singlesScale, multiplesScale = None, None
	uniqueStates = None
	indexes = None

	def __init__(self, simulation, singlesWithDiscreteNum, multiplesWithDiscreteNum):
		# separate the names and options for fields
		singlesFields = []
		self.singlesDiscrete = dict()
		self.singlesScale = dict()
		for value in singlesWithDiscreteNum:
			assert isinstance(value, discreteState)
			fieldName = value.name
			singlesFields.append(fieldName)
			self.singlesDiscrete[fieldName] = value.discreteOptions
			self.singlesScale[fieldName] = value.scale
		multiplesFields = []
		self.multiplesDiscrete = dict()
		for value in multiplesWithDiscreteNum:
			assert isinstance(value, discreteState)
			fieldName = value.name
			multiplesFields.append(fieldName)
			self.multiplesDiscrete[fieldName] = value.discreteOptions
			self.multiplesScale[fieldName] = value.scale

		# # compute all indexes
		# computeIndeces()

		systemState.__init__(self, simulation=simulation, singles=singlesFields, multiples=multiplesFields)

	# def discretise(self):
	# 	for i in range(len(self.currentState)):
	# 		self.currentState[i] = discretisedSystemState.binariseValue(self.currentState[i])

	@staticmethod
	def discretiseValue(value, bins, scale):
		if scale:
			assert value <= 1
			return round(value * (bins - 1))
		else:
			assert value < bins
			return value

	def setField(self, field, value):
		assert field in self.dictRepresentation
		debug.out("set %s to %s: %s" % (field, value, self.dictRepresentation[field][:]))
		if isinstance(value, list):
			for i in range(len(value)):
				self.dictRepresentation[field][i] = discretisedSystemState.discretiseValue(value[i], self.multiplesDiscrete[field], self.multiplesScale[field])
		else:
			self.dictRepresentation[field][:] = discretisedSystemState.discretiseValue(value, self.singlesDiscrete[field], self.singlesScale[field])

		debug.out("set %s to %s: %s" % (field, value, self.dictRepresentation[field][:]))

	def getUniqueStates(self):
		if self.uniqueStates is None:
			self.uniqueStates = 1
			for single in self.singlesDiscrete:
				self.uniqueStates *= self.singlesDiscrete[single]
			for multiple in self.multiplesDiscrete:
				self.uniqueStates *= self.multiplesDiscrete[multiple] ** constants.NUM_DEVICES
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
	def getIndex(self):
		out = 0

		multipleOverallStates = 1 # placeholder until i add multiple states again
		for i in range(len(self.singles)):
			# calculate multiplication factor based on remaining states' options
			restMultiplier = 1
			if i < len(self.singles) - 1:
				for j in range(i + 1, len(self.singles)):
					restMultiplier *= self.singlesDiscrete[self.singles[j]]

			out += self.dictRepresentation[self.singles[i]] * restMultiplier
			# print(self.singles[i], self.dictRepresentation[self.singles[i]], restMultiplier, out)
		assert self.multiples == []
		return out

	def getStateDescription(self, index):
		description = ""
		for i in range(len(self.singles)):
			# calculate multiplication factor based on remaining states' options
			restMultiplier = 1
			if i < len(self.singles) - 1:
				for j in range(i + 1, len(self.singles)):
					restMultiplier *= self.singlesDiscrete[self.singles[j]]

			field = int(index / restMultiplier)
			if index >= restMultiplier:
				index -= restMultiplier * field
			description += "%s=%s " % (self.singles[i], field)
				# print(index)
		return description


	def setState(self, arrayState):
		self.currentState = np.array(arrayState, dtype=np.dtype('b'))
		self.createDictionaryRepresentation()

class discreteState:
	name = None
	discreteOptions = None
	scale = None

	def __init__(self, name, discreteOptions, scale=True):
		self.name = name
		self.discreteOptions = discreteOptions
		self.scale = scale
