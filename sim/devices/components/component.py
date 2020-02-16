import sim.devices.components.powerState
import sim.simulations.constants


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
		self.state = sim.devices.components.powerState.SLEEP

	# def activeEnergy(self, time):
	# 	print (time)
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.activeCurrent])

	# def idleEnergy(self, time):
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.idleCurrent])

	def busy(self):
		return self.state == sim.devices.components.powerState.ACTIVE

	# change power states
	def active(self):
		self.state = sim.devices.components.powerState.ACTIVE
	def isActive(self):
		return self.state == sim.devices.components.powerState.ACTIVE
	def idle(self):
		self.state = sim.devices.components.powerState.IDLE
	def isIdle(self):
		return self.state == sim.devices.components.powerState.IDLE
	def sleep(self):
		self.state = sim.devices.components.powerState.SLEEP
	def isSleeping(self):
		return self.state == sim.devices.components.powerState.SLEEP

	def getPowerState(self):
		return self.state

	def colour(self):
		if self.state == sim.devices.components.powerState.IDLE:
			return self.idleColour
		elif self.state == sim.devices.components.powerState.ACTIVE:
			return self.busyColour
		elif self.state == sim.devices.components.powerState.SLEEP:
			return self.sleepColour
		else:
			raise Exception("Unknown power state")
		

	# power level right now
	def power(self):
		if self.state == sim.devices.components.powerState.IDLE:
			powerList = self.idlePower
		elif self.state == sim.devices.components.powerState.ACTIVE:
			powerList = self.activePower
		elif self.state == sim.devices.components.powerState.SLEEP:
			powerList = self.sleepPower
		else:
			raise Exception("Unknown power state: " + str(self.state))

		# compute total power for all lines
		return component._total(powerList)

	# helper function for totalling a generated list
	@staticmethod
	def _total(lst):
		total = 0
		for element in lst:
			total+= element.gen()
		return total