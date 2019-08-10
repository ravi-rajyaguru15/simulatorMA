import sim.constants 
from sim.component import component

import random
import numpy as np

class mrf(component):
	busyColour = (0, 1, 0, 1)
	idleColour = (0, 0.5, 0, 1)
	sleepColour = (0, 0.2, 0, 1)

	rxCurrent, txCurrent = [sim.constants.WIRELESS_RX_CURRENT], [sim.constants.WIRELESS_TX_CURRENT]
	transmissionRate = sim.constants.WIRELESS_SPEED

	def __init__(self):
		component.__init__(
			self,
			voltage = [sim.constants.MCU_VOLTAGE],
			activeCurrent = None, # active is either RX or TX
			idleCurrent = [sim.constants.WIRELESS_IDLE_CURRENT],
			sleepCurrent = [sim.constants.WIRELESS_SLEEP_CURRENT],
			)
		
	def tx(self):
		self.state = sim.powerState.TX

	def rx(self):
		self.state = sim.powerState.RX

	# special states
	def colour(self):
		if self.state == sim.powerState.TX:
			return self.busyColour
		elif self.state == sim.powerState.RX:
			return self.busyColour
		else:
			# pass it up to the parent
			return component.colour(self)
	

	def current(self):
		if self.state == sim.powerState.TX:
			return self.txCurrent
		elif self.state == sim.powerState.RX:
			return self.rxCurrent
		else:
			# pass it up to the parent
			return component.current(self)
	
						# def activeEnergy(self, time):
	# 	print ("special mrf active time")
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.activeCurrent])


	# def __init__(self, txCurrent=None, rxCurrent = None):

	# 	if txCurrent is None:
	# 		self.txCurrent = sim.constants.WIRELESS_CURRENT)
	# 	else:
	# 		self.txCurrent = txCurrent


	# 	if rxCurrent is None:
	# 		self.rxCurrent = sim.constants.WIRELESS_CURRENT)
	# 	else:
	# 		self.rxCurrent = rxCurrent

	# def txEnergy(self, duration):
	# 	return duration * np.dot([voltage.gen() for voltage in self.voltage], [self.txCurrent.gen()])

		# return duration * self.voltage[0].gen() * self.txCurrent.gen() / 1000.

	# def rxEnergy(self, duration):
	# 	return duration * np.dot([voltage.gen() for voltage in self.voltage], [self.rxCurrent.gen()])

	def rxtxLatency(self, messageSize):
		# print 'size', messageSize, 'lat', messageSize / 1024. / self.transmissionRate)
		return messageSize / 1024. / self.transmissionRate.gen()