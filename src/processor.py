import constants

import numpy as np

class processor:
	voltage = activeCurrent = idleCurrent = processingSpeed = None

	def __init__(self, voltage, activeCurrent, idleCurrent, sleepCurrent, processingSpeed):
		self.voltage = voltage
		self.activeCurrent = activeCurrent
		self.idleCurrent = idleCurrent
		self.sleepCurrent = sleepCurrent
		self.processingSpeed = processingSpeed

	def activeEnergy(self, time):
		return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.activeCurrent])

	def idleEnergy(self, time):
		return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.idleCurrent])

	def processingTime(self, samples):
		return samples / self.processingSpeed.gen()