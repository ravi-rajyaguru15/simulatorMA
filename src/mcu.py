import constants

class mcu:
	voltage = constants.MCU_VOLTAGE
	
	activeCurrent = constants.MCU_ACTIVE_CURRENT
	idleCurrent = constants.MCU_IDLE_CURRENT

	messageOverheadLatency = constants.MCU_MESSAGE_OVERHEAD_LATENCY

	processingSpeed = constants.MCU_PROCESSING_SPEED

	def __init__(self):

		# self.processingCurrent = processingCurrent

		# self.messageOverheadLatency = messageOverheadLatency
		pass

	def overheadEnergy(self):
		return self.messageOverheadLatency.gen() * self.activeCurrent.gen() / 1000. * self.voltage.gen()

	def activeEnergy(self, time):
		return time * self.voltage.gen() * self.activeCurrent.gen()

	def processingTime(self, samples):
		return samples / self.processingSpeed.gen()