import sim.constants
from sim.component import component

import numpy as np
import matplotlib.pyplot as pp

class processor(component):
	processingSpeed = None

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
		# print("processing", samples, self.processingSpeed.gen(), task.complexity, samples / self.processingSpeed.gen() * task.complexity, )
		return samples / self.processingSpeed.gen() * task.complexity