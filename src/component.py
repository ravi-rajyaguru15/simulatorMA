import constants
from powerState import powerStates

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
		self.state = powerStates.IDLE

	# def activeEnergy(self, time):
	# 	print (time)
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.activeCurrent])

	# def idleEnergy(self, time):
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.idleCurrent])

	# current level right now
	def current(self):
		if self.state == powerStates.IDLE:
			return self.idleCurrent
		elif self.state == powerStates.ACTIVE:
			return self.activeCurrent

	# current power level of this component
	def power(self):
				
		return np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.current()])