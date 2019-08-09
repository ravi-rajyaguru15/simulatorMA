import random

import sim.constants

from sim.node import node
from sim.mcu import mcu
from sim.mrf import mrf
from sim.result import result

class endDevice(node):
	def __repr__(self):
		return "End Device {0}".format(self.index)

	def __init__(self, queue, index, alwaysHardwareAccelerate):

		self.mcu = mcu()
		self.mrf = mrf()

		node.__init__(self, queue, index, nodeType=constants.END_DEVICE, components=[self.mcu, self.mrf], alwaysHardwareAccelerate=alwaysHardwareAccelerate)

	# def processingEnergy(self, duration):
	# 	return self.mcu.activeEnergy(duration) + self.mrf.idleEnergy(duration)

