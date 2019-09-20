import constants 
from component import component

import random
import numpy as np

class mrf(component):
	busyColour = (0, 1, 0, 1)
	idleColour = (0, 0.5, 0, 1)

	busy = None
	rxCurrent, txCurrent = constants.WIRELESS_RX_CURRENT, constants.WIRELESS_TX_CURRENT
	transmissionRate = constants.WIRELESS_SPEED

	def __init__(self):
		self.busy = False

		component.__init__(
			self,
			voltage = [constants.MCU_VOLTAGE],
			activeCurrent = [0],
			idleCurrent = [constants.WIRELESS_IDLE_CURRENT],
			sleepCurrent = [constants.WIRELESS_SLEEP_CURRENT],
			)

	def activeEnergy(self, time):
		print ("special mrf active time")
		return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.activeCurrent])


	# def __init__(self, txCurrent=None, rxCurrent = None):

	# 	if txCurrent is None:
	# 		self.txCurrent = constants.WIRELESS_CURRENT)
	# 	else:
	# 		self.txCurrent = txCurrent


	# 	if rxCurrent is None:
	# 		self.rxCurrent = constants.WIRELESS_CURRENT)
	# 	else:
	# 		self.rxCurrent = rxCurrent

	def txEnergy(self, duration):
		return duration * np.dot([voltage.gen() for voltage in self.voltage], [self.txCurrent.gen()])

		# return duration * self.voltage[0].gen() * self.txCurrent.gen() / 1000.

	def rxEnergy(self, duration):
		return duration * np.dot([voltage.gen() for voltage in self.voltage], [self.rxCurrent.gen()])

	def rxtxLatency(self, messageSize):
		# print 'size', messageSize, 'lat', messageSize / 1024. / self.transmissionRate)
		return messageSize / 1024. / self.transmissionRate.gen()