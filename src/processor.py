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

	def createRectangle(self, location, size):
		self.rectangle = pp.Rectangle((location[0] - size[0]/2, location[1] - size[1]/2), size[0], size[1], fill=True)


	def processingTime(self, samples):
		return samples / self.processingSpeed.gen()

