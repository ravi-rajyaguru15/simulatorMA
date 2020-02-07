import sim.simulations.constants
from sim.devices.components import powerPolicy
from sim.devices.components.processor import processor
from sim.simulations import constants


class mcu(processor):
	busyColour = (1, 0, 0, 1)
	idleColour = (0.5, 0, 0, 1)
	sleepColour = (0.2, 0, 0, 1)

	messageOverheadLatency = None

	def __init__(self, owner):
		processor.__init__(self, owner,
						   # voltage = [platform.MCU_VOLTAGE],
						   activePower = [owner.platform.MCU_ACTIVE_POWER],
						   idlePower = [owner.platform.MCU_IDLE_POWER],
						   sleepPower = [owner.platform.MCU_SLEEP_POWER],
						   processingSpeed = owner.platform.MCU_PROCESSING_SPEED,
						   idleTimeout = sim.simulations.constants.MCU_IDLE_SLEEP)
		self.messageOverheadLatency = owner.platform.MCU_MESSAGE_OVERHEAD_LATENCY


	def timeOutSleep(self):
		if constants.MCU_POWER_PLAN == powerPolicy.IDLE_TIMEOUT:
			processor.timeOutSleep(self)

	def overheadTime(self):
		return self.messageOverheadLatency.gen()

	# def overheadEnergy(self, time):
	# 	return time * self.activeCurrent.gen() / 1000. * self.voltage.gen()

	# def activeEnergy(self, time):
	# 	return time * self.voltage.gen() * self.activeCurrent.gen()

	# def processingTime(self, samples):
	# 	return samples / self.processingSpeed.gen()