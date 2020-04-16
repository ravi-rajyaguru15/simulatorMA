from sim import debug
# from sim.devices.components import component
from sim.devices.components.component import component
from sim.devices.components.powerState import RECONFIGURING
from sim.devices.components.processor import processor
from sim.simulations import constants


class fpga(processor):
	busyColour = (0, 0, 1, 1)
	idleColour = (0, 0, 0.5, 1)
	sleepColour = (0, 0, 0.2, 1)
	reconfigurationColour = (0, 0, 0.25, 1)

	configTimes = dict()
	lastConfigTime = None

	currentConfig = None
	reconfigurationPower = None
	# [self.platform.FPGA_RECONFIGURATION_INT_Power, self.platform.FPGA_RECONFIGURATION_AUX_CURRENT]

	def __init__(self, owner):
		self.reconfigurationPower = [owner.platform.FPGA_RECONFIGURATION_INT_POWER, owner.platform.FPGA_RECONFIGURATION_AUX_POWER]

		processor.__init__(self, owner,
			# voltage = [platform.FPGA_ INT_VOLTAGE, platform.FPGA_AUX_VOLTAGE],
			activePower = [owner.platform.FPGA_ACTIVE_INT_POWER, owner.platform.FPGA_ACTIVE_AUX_POWER],
			idlePower = [owner.platform.FPGA_IDLE_INT_POWER, owner.platform.FPGA_IDLE_AUX_POWER],
			sleepPower = [owner.platform.FPGA_SLEEP_INT_POWER, owner.platform.FPGA_SLEEP_AUX_POWER],
			processingSpeed = owner.platform.FPGA_PROCESSING_SPEED,
			idleTimeout = constants.FPGA_IDLE_SLEEP)
	#
	# def timeOutSleep(self):
	# 	# do not sleep until done with batch
	# 	if self.owner.currentBatch is None:
	# 		# check if it's time to sleep device
	# 		if constants.FPGA_POWER_PLAN == powerPolicy.IDLE_TIMEOUT:
	# 			processor.timeOutSleep(self)
	# 		elif constants.FPGA_POWER_PLAN == powerPolicy.IMMEDIATELY_OFF and self.isIdle():
	# 			self.sleep()
			
	def reset(self):
		self.lastConfigTime = None
		self.setConfig(None)
		processor.reset(self)
		self.configTimes = dict()

	# power states
	def reconfigure(self, task):
		self.setConfig(task)
		debug.out("changed fpga config to %s" % task.identifier)
		self.busyColour = task.colour
		# print ("changed fpga colour")
		self.__state = RECONFIGURING

	# encode current config for 0: none; 1,2,3: different tasks
	def getCurrentConfigIndex(self):
		if self.currentConfig is None:
			return 0
		else:
			return self.currentConfig.identifier

	# loses configuration when it sleeps
	def sleep(self):
		self.setConfig(None)
		processor.sleep(self)

	def setConfig(self, configuration):

		# add config times to logs
		if self.lastConfigTime is not None:
			# only increment time when it has been configured before
			self.incrementConfigTime(self.currentConfig, self.owner.currentTime.current - self.lastConfigTime)

		# update config to new config
		self.currentConfig = configuration
		self.lastConfigTime = self.owner.currentTime.current

	def incrementConfigTime(self, task, increment):
		assert increment >= 0
		if task not in self.configTimes:
			self.configTimes[task] = increment
		else:
			self.configTimes[task] += increment

	def getConfigTime(self, task):
		if task not in self.configTimes:
			return 0
		else:
			return self.configTimes[task]
		# print("incremented", task, "on", self.owner, "by", increment)

	def isReconfiguring(self):
		return self.getPowerState() == RECONFIGURING
	# def current(self):
	# 	if self.state == sim.powerState.RECONFIGURING:
	# 		return self.reconfigurationCurrent
	# 	else:
	# 		return component.current(self)

	def power(self):
		if self.isReconfiguring():
			return component._total(self.reconfigurationPower)
		else:
			return component.power(self)

	def colour(self):
		if self.isReconfiguring():
			return self.reconfigurationColour
		else:
			return component.colour(self)

	def isConfigured(self, task):
		assert task is not None
		return self.currentConfig == task

	# def reconfigurationEnergy(self, time):
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.reconfigurationCurrent])

 