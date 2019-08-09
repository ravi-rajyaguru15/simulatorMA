import sim.constants
from sim.processor import processor

class mcu(processor):
	busyColour = (1, 0, 0, 1)
	idleColour = (0.5, 0, 0, 1)
	sleepColour = (0.2, 0, 0, 1)

	messageOverheadLatency = None

	def __init__(self):
		processor.__init__(self,
			voltage = [sim.constants.MCU_VOLTAGE],
			activeCurrent = [sim.constants.MCU_ACTIVE_CURRENT],
			idleCurrent = [sim.constants.MCU_IDLE_CURRENT],
			sleepCurrent = [sim.constants.MCU_SLEEP_CURRENT],
			processingSpeed = sim.constants.MCU_PROCESSING_SPEED)
		self.messageOverheadLatency = sim.constants.MCU_MESSAGE_OVERHEAD_LATENCY

	def overheadTime(self):
		return self.messageOverheadLatency.gen()

	# def overheadEnergy(self, time):
	# 	return time * self.activeCurrent.gen() / 1000. * self.voltage.gen()

	# def activeEnergy(self, time):
	# 	return time * self.voltage.gen() * self.activeCurrent.gen()

	# def processingTime(self, samples):
	# 	return samples / self.processingSpeed.gen()