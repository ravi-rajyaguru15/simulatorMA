import constants

import numpy as np

class component:
	voltage = activeCurrent = idleCurrent = None

	def __init__(self, voltage, activeCurrent, idleCurrent, sleepCurrent):
		self.voltage = voltage
		self.activeCurrent = activeCurrent
		self.idleCurrent = idleCurrent
		self.sleepCurrent = sleepCurrent

	def activeEnergy(self, time):
		print time
		return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.activeCurrent])

	def idleEnergy(self, time):
		return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.idleCurrent])
