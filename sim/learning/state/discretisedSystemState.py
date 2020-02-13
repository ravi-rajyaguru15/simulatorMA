import numpy as np

from sim.learning.state.systemState import systemState
from sim.simulations import constants


class discretisedSystemState(systemState):
	singlesWidths, multiplesWidths = None, None
	uniqueStates = None

	def __init__(self, simulation, singlesWithBitwidths, multiplesWithBitwidths):
		# separate the names and bitwidths for fields
		singlesFields = []
		self.singlesWidths = dict()
		for value in singlesWithBitwidths:
			assert isinstance(value, tuple)
			fieldName = value[0]
			singlesFields.append(fieldName)
			self.singlesWidths[fieldName] = value[1]
		multiplesFields = []
		self.multiplesWidths = dict()
		for value in multiplesWithBitwidths:
			assert isinstance(value, tuple)
			fieldName = value[0]
			multiplesFields.append(fieldName)
			self.multiplesWidths[fieldName] = value[1]

		print("creating system state with", singlesFields, multiplesFields)
		systemState.__init__(self, simulation=simulation, singles=singlesFields, multiples=multiplesFields)

	# def discretise(self):
	# 	for i in range(len(self.currentState)):
	# 		self.currentState[i] = discretisedSystemState.binariseValue(self.currentState[i])

	@staticmethod
	def discretiseValue(value, bins):
		return round(value * bins)

	def setField(self, field, value):
		assert field in self.dictRepresentation
		if isinstance(value, list):
			for i in range(len(value)):
				self.dictRepresentation[field][i] = discretisedSystemState.discretiseValue(value[i], self.multiplesWidths[field])
		else:
			self.dictRepresentation[field][:] = discretisedSystemState.discretiseValue(value, self.singlesWidths[field])

	def getUniqueStates(self):
		if self.uniqueStates == None:
			self.uniqueStates = 1
			for single in self.singlesWidths:
				self.uniqueStates *= self.singlesWidths[single]
			for multiple in self.multiplesWidths:
				self.uniqueStates *= self.multiplesWidths[multiple] ** constants.NUM_DEVICES
		return self.uniqueStates

	def __addIndex(self, currentIndex, field, multiple):
		value = self.dictRepresentation[field]
		if multiple:
			width = self.multiplesWidths[field]
		else:
			width = self.singlesWidths[field]
		print("adding", field, value, width, currentIndex)
		return (currentIndex << width) + value

	# convert currentState to an integer index
	def getIndex(self):
		out = 0
		raise Exception("error with indexes way too high... need to compute total index better") # compute offset for each nonchosen choice
		print("\nget index")
		# first go through singles, then multiples and compute an overall
		j = 0

		for i in range(len(self.singles)):
			out = self.__addIndex(out, self.singles[i], multiple=False)
		for i in range(len(self.multiples)):
			out = self.__addIndex(out, self.multiples[i], multiple=False)
		# print("index", out, self.currentState, self.currentState[0], self.currentState[-1])
		return out

	def setState(self, arrayState):
		self.currentState = np.array(arrayState, dtype=np.dtype('b'))
		self.createDictionaryRepresentation()


