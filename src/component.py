import constants
import powerState

import numpy as np

class component:
	voltage = activeCurrent = idleCurrent = None
	
	state = None

	def __init__(self, voltage, activeCurrent, idleCurrent, sleepCurrent):
		self.voltage = voltage
		self.activeCurrent = activeCurrent
		self.idleCurrent = idleCurrent
		self.sleepCurrent = sleepCurrent

		# start idle
		self.state = powerState.SLEEP

	# def activeEnergy(self, time):
	# 	print (time)
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.activeCurrent])

	# def idleEnergy(self, time):
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.idleCurrent])

	def busy(self):
		return self.state != powerState.IDLE

	# change power states
	def active(self):
		self.state = powerState.ACTIVE
	def idle(self):
		self.state = powerState.IDLE
	def sleep(self):
		self.state = powerState.SLEEP

	def colour(self):
		if self.state == powerState.IDLE:
			return self.idleColour
		elif self.state == powerState.ACTIVE:
			return self.busyColour
		elif self.state == powerState.SLEEP:
			return self.sleepColour
		else:
			raise Exception("Unknown power state")
		

	# current level right now
	def current(self):
		if self.state == powerState.IDLE:
			return self.idleCurrent
		elif self.state == powerState.ACTIVE:
			return self.activeCurrent
		elif self.state == powerState.SLEEP:
			return self.sleepCurrent
		else:
			raise Exception("Unknown power state")

	# current power level of this component
	def power(self):
		return np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.current()])