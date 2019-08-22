import sim.constants
from sim.component import component

import numpy as np
import matplotlib.pyplot as pp

class processor(component):
	processingSpeed = None
	idleTime = None
	idleTimeout = None

	rectangle = None

	def __init__(self, activePower, idlePower, sleepPower, processingSpeed, idleTimeout):
		component.__init__(
			self,
			# voltage = voltage,
			activePower = activePower,
			idlePower = idlePower,
			sleepPower = sleepPower)

		self.processingSpeed = processingSpeed
		self.idleTime = 0
		self.idleTimeout = idleTimeout

	def processingTime(self, samples, task):
		assert(task is not None)
		# print("processing", samples, self.processingSpeed.gen(), task.complexity, samples / self.processingSpeed.gen() * task.complexity, )
		return samples / self.processingSpeed.gen() * task.complexity

	def timeOutSleep(self):
		if self.isIdle():
			if self.idleTime >= self.idleTimeout:
				self.sleep()
				sim.debug.out("PROCESSOR SLEEP")
			else:
				self.idleTime += sim.constants.TD
		else:
			self.idleTime = 0
		
		sim.debug.out("idleTime: {}".format(self.idleTime))
