import numpy as np

from sim.learning.state.systemState import systemState

class binarySystemState(systemState):
	def binarise(self):
		for i in range(len(self.currentState)):
			self.currentState[i] = binarySystemState.binariseValue(self.currentState[i])

	@staticmethod
	def binariseValue(value):
		if value < 0: value = 0
		if value > 1: value = 1
		return value

	def setField(self, field, value):
		assert field in self.dictRepresentation
		if isinstance(value, list):
			for i in range(len(value)):
				self.dictRepresentation[field][i] = binarySystemState.binariseValue(value[i])
		else:
			self.dictRepresentation[field][:] = binarySystemState.binariseValue(value)

	# convert currentState to an integer index
	def getIndex(self):
		out = 0
		for i in self.currentState:
			assert 1 >= i >= 0
			out = (out << 1) | i
		print("index", out, self.currentState)
		return out

	def setState(self, arrayState):
		self.currentState = np.array(arrayState, dtype=np.dtype('b'))
		self.createDictionaryRepresentation()


