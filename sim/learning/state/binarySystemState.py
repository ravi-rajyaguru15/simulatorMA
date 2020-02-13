import numpy as np

from sim.learning.state.systemState import systemState
from sim.simulations import constants


class binarySystemState(systemState):
	def binarise(self):
		for i in range(len(self.currentState)):
			self.currentState[i] = binarySystemState.binariseValue(self.currentState[i])

	@staticmethod
	def binariseValue(value):
		if value < 0: value = 0
		if value > 1: value = 1
		return value

	def getUniqueStates(self):
		return 2 ** (len(self.singles) + len(self.multiples) * constants.NUM_DEVICES)


	def setField(self, field, value):
		print("field", field, "in", self.dictRepresentation)
		assert field in self.dictRepresentation
		if isinstance(value, list):
			for i in range(len(value)):
				self.dictRepresentation[field][i] = binarySystemState.binariseValue(value[i])
		else:
			self.dictRepresentation[field][:] = binarySystemState.binariseValue(value)

	# convert currentState to an integer index
	def getIndex(self):
		out = 0
		for i in self.currentState[::-1]:
			assert 1 >= i >= 0
			out = (out << 1) | i
		# print("index", out, self.currentState, self.currentState[0], self.currentState[-1])
		return out

	def setState(self, arrayState):
		self.currentState = np.array(arrayState, dtype=np.dtype('b'))
		self.createDictionaryRepresentation()


