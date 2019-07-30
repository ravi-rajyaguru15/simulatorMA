import random
import constants

from node import node
from mcu import mcu
from mrf import mrf
from result import result

class endDevice(node):

	def __init__(self, queue, index, alwaysHardwareAccelerate):

		self.mcu = mcu()
		self.mrf = mrf()

		node.__init__(self, queue, index, nodeType=constants.END_DEVICE, components=[self.mcu, self.mrf], alwaysHardwareAccelerate=alwaysHardwareAccelerate)

	def processingEnergy(self, duration):
		return self.mcu.activeEnergy(duration) + self.mrf.idleEnergy(duration)

