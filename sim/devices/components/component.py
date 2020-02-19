from sim.devices.components.powerState import SLEEP, ACTIVE, IDLE


class component:
	voltage = activePower = idlePower = None
	
	__state = None
	owner = None
	# platform = None
	latestActive = None

	def __init__(self, owner, activePower, idlePower, sleepPower):
		# self.platform = platform
		self.owner = owner

		# self.voltage = voltage
		self.activePower = activePower
		self.idlePower = idlePower
		self.sleepPower = sleepPower

		# start idle
		self.__state = SLEEP
		latestActive = None

	# def activeEnergy(self, time):
	# 	print (time)
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.activeCurrent])

	# def idleEnergy(self, time):
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.idleCurrent])

	def busy(self):
		return self.__state == ACTIVE

	# change power states
	def active(self):
		self.__state = ACTIVE
	def isActive(self):
		return self.__state == ACTIVE
	def idle(self):
		# if was active: update latest active time (used for sleeping)
		if self.__state == ACTIVE:
			self.latestActive = self.owner.currentTime.current
		self.__state = IDLE
	def isIdle(self):
		return self.__state == IDLE
	def sleep(self):
		self.__state = SLEEP
	def isSleeping(self):
		return self.__state == SLEEP

	def setPowerState(self, newState):
		self.__state = newState
	def getPowerState(self):
		return self.__state

	def colour(self):
		if self.__state == IDLE:
			return self.idleColour
		elif self.__state == ACTIVE:
			return self.busyColour
		elif self.__state == SLEEP:
			return self.sleepColour
		else:
			raise Exception("Unknown power state")
		

	# power level right now
	def power(self):
		if self.__state == IDLE:
			powerList = self.idlePower
		elif self.__state == ACTIVE:
			powerList = self.activePower
		elif self.__state == SLEEP:
			powerList = self.sleepPower
		else:
			raise Exception("Unknown power state: " + str(self.__state))

		# compute total power for all lines
		return component._total(powerList)

	# helper function for totalling a generated list
	@staticmethod
	def _total(lst):
		total = 0
		for element in lst:
			total+= element.gen()
		return total