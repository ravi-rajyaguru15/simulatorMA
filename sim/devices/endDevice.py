from sim.devices.components.mcu import mcu
from sim.devices.components.mrf import mrf
from sim.devices.node import node


class endDevice(node):
	def __repr__(self):
		return "End Device {0}".format(self.index)

	def __init__(self, platform, queue, index, alwaysHardwareAccelerate):

		self.mcu = mcu()
		self.mrf = mrf()

		node.__init__(self, platform, queue, index, components=[self.mcu, self.mrf], alwaysHardwareAccelerate=alwaysHardwareAccelerate)

	# def processingEnergy(self, duration):
	# 	return self.mcu.activeEnergy(duration) + self.mrf.idleEnergy(duration)

