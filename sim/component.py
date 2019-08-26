import sim.constants
import sim.powerState

import numpy as np

class component:
	voltage = activePower = idlePower = None
	
	state = None
	owner = None
	# platform = None

	def __init__(self, owner, activePower, idlePower, sleepPower):
		# self.platform = platform
		self.owner = owner

		# self.voltage = voltage
		self.activePower = activePower
		self.idlePower = idlePower
		self.sleepPower = sleepPower

		# start idle
		self.state = sim.powerState.SLEEP

	# def activeEnergy(self, time):
	# 	print (time)
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.activeCurrent])

	# def idleEnergy(self, time):
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.idleCurrent])

	def busy(self):
		return self.state == sim.powerState.ACTIVE

	# change power states
	def active(self):
		self.state = sim.powerState.ACTIVE
	def isActive(self):
		return self.state == sim.powerState.ACTIVE
	def idle(self):
		self.state = sim.powerState.IDLE
	def isIdle(self):
		return self.state == sim.powerState.IDLE
	def sleep(self):
		self.state = sim.powerState.SLEEP
	def isSleeping(self):
		return self.state == sim.powerState.SLEEP

	def colour(self):
		if self.state == sim.powerState.IDLE:
			return self.idleColour
		elif self.state == sim.powerState.ACTIVE:
			return self.busyColour
		elif self.state == sim.powerState.SLEEP:
			return self.sleepColour
		else:
			raise Exception("Unknown power state")
		

	# power level right now
	def power(self):
		if self.state == sim.powerState.IDLE:
			return np.sum(power.gen() for power in self.idlePower)
		elif self.state == sim.powerState.ACTIVE:
			return np.sum(power.gen() for power in self.activePower)
		elif self.state == sim.powerState.SLEEP:
			return np.sum(power.gen() for power in self.sleepPower)
		else:
			raise Exception("Unknown power state: " + str(self.state))

	# # Power power level of this component
	# def power(self):
	# 	# print (self)
	# 	# print(self.voltage, self.current())
	# 	return np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.current()])