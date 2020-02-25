import sys
import traceback
from random import choice

from sim import debug


class action:
	name = None
	targetDevice = None
	targetDeviceIndex = None
	local = False
	index = None
	immediate = None

	def __init__(self, name, offloading=False, immediate=False):
		self.name = name
		if not offloading:
			self.local = True
		else:
			# self.name = "{} {}".format(name, targetIndex)
			# self.targetDeviceIndex = targetIndex
			self.local = False
		self.immediate = immediate

	def __repr__(self):
		return self.name

	def offloadingToTarget(self, targetIndex=None): return False

	# update device based on latest picked device index
	def updateTargetDevice(self, owner, offloadingDevices):
		if self.local:
			assert owner is not None
			self.targetDeviceIndex = owner.index
			self.targetDevice = owner
		else:
			# assert self.targetDeviceIndex is not None
			debug.out("updating target device for action: %s [%s]" % (str(self), offloadingDevices))
			assert offloadingDevices is not None

			self.targetDevice = choice(offloadingDevices)
			# self.targetDevice = None
			# # find device based on its index
			# for device in offloadingDevices:
			# 	if device.index == self.targetDeviceIndex:
			# 		self.targetDevice = device
			# 		break

			if self.targetDevice is None:
				print("updateDevice failed!", self, offloadingDevices, self.targetDeviceIndex)

			assert self.targetDevice is not None
	# self.targetDevice = devices[self.targetDeviceIndex]

# def setTargetDevice(self, device):
# 	self.targetDevice = device


class offloading(action):
	# destinations = None

	def __init__(self):
		super().__init__("Offload", offloading=True)
		# self.destinations = destinations

	# def offloadingToTarget(self, index):
	# 	return self.targetDeviceIndex == index


class localAction(action):
	def __init__(self, immediate):
		if immediate:
			name = "Local"
		else:
			name = "Batch"
		super().__init__(name, immediate=immediate)


OFFLOADING = offloading()
BATCH = localAction(False)  # TODO: wait does nothing
LOCAL = localAction(True)

