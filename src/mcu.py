import constants
from processor import processor

class mcu(processor):
	messageOverheadLatency = None

	def __init__(self):
		processor.__init__(self,
			voltage = [constants.MCU_VOLTAGE],
			activeCurrent = [constants.MCU_ACTIVE_CURRENT],
			idleCurrent = [constants.MCU_IDLE_CURRENT],
			sleepCurrent = [constants.MCU_SLEEP_CURRENT],
			processingSpeed = constants.MCU_PROCESSING_SPEED)
		self.messageOverheadLatency = constants.MCU_MESSAGE_OVERHEAD_LATENCY

	def overheadTime(self):
		return self.messageOverheadLatency.gen()

	# def overheadEnergy(self, time):
	# 	return time * self.activeCurrent.gen() / 1000. * self.voltage.gen()

	# def activeEnergy(self, time):
	# 	return time * self.voltage.gen() * self.activeCurrent.gen()

	# def processingTime(self, samples):
	# 	return samples / self.processingSpeed.gen()