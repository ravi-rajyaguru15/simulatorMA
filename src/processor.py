import constants
from component import component

import numpy as np
import matplotlib.pyplot as pp

class processor(component):
	processingSpeed = None
	busy = False

	rectangle = None

	def __init__(self, voltage, activeCurrent, idleCurrent, sleepCurrent, processingSpeed):
		component.__init__(
			self,
			voltage = voltage,
			activeCurrent = activeCurrent,
			idleCurrent = idleCurrent,
			sleepCurrent = sleepCurrent)

		self.processingSpeed = processingSpeed

	def processingTime(self, samples, task):
		assert(task is not None)
		return samples / self.processingSpeed.gen() * task.complexity


