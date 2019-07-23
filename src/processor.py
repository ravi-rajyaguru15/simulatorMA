import constants
from component import component

import numpy as np

class processor(component):
	processingSpeed = None

	def __init__(self, voltage, activeCurrent, idleCurrent, sleepCurrent, processingSpeed):
		component.__init__(
			self,
			voltage = voltage,
			activeCurrent = activeCurrent,
			idleCurrent = idleCurrent,
			sleepCurrent = sleepCurrent)

		self.processingSpeed = processingSpeed

	def processingTime(self, samples):
		return samples / self.processingSpeed.gen()