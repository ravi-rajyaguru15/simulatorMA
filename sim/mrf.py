import sim.constants 
from sim.component import component

import random
import numpy as np

class mrf(component):
	busyColour = (0, 1, 0, 1)
	idleColour = (0, 0.5, 0, 1)
	sleepColour = (0, 0.2, 0, 1)

	rxPower, txPower = None, None
	transmissionRate = None

	def __init__(self, owner):
		self.rxPower, self.txPower = [owner.platform.WIRELESS_RX_CURRENT], [owner.platform.WIRELESS_TX_CURRENT]
		self.transmissionRate = owner.platform.WIRELESS_SPEED
		
		component.__init__(
			self, owner,
			# voltage = [platform.MCU_VOLTAGE],
			activePower = None, # active is either RX or TX
			idlePower = [owner.platform.WIRELESS_IDLE_POWER],
			sleepPower = [owner.platform.WIRELESS_SLEEP_POWER],
			)
	
	def busy(self):
		return self.state == sim.powerState.TX or self.state == sim.powerState.RX or component.busy(self)

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
	
	def power(self):
		if self.state == sim.powerState.TX:
			return np.sum([power.gen() for power in self.txPower])
		elif self.state == sim.powerState.RX:
			return np.sum([power.gen() for power in self.rxPower])

		else:
			# pass it up to the parent
			return component.power(self)
    		

	# def current(self):
	# 	if self.state == sim.powerState.TX:
	# 		return self.txCurrent
	# 	elif self.state == sim.powerState.RX:
	# 		return self.rxCurrent
	# 	else:
	# 		# pass it up to the parent
	# 		return component.current(self)
	
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