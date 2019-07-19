import constants

class mcu:
	voltage = constants.MCU_VOLTAGE
	
	activeCurrent = constants.MCU_ACTIVE_CURRENT
	idleCurrent = constants.MCU_IDLE_CURRENT

	messageOverheadLatency = constants.MCU_MESSAGE_OVERHEAD_LATENCY

	processingSpeed = constants.MCU_PROCESSING_SPEED

	def __init__(this):

		# this.processingCurrent = processingCurrent

		# this.messageOverheadLatency = messageOverheadLatency
		pass

	def overheadEnergy(this):
		return constants.randomise(this.messageOverheadLatency) * constants.randomise(this.activeCurrent) / 1000. * constants.randomise(this.voltage)

	def activeEnergy(this, time):
		return time * constants.randomise(this.voltage) * constants.randomise(this.activeCurrent)

	def processingTime(this, samples):
		return samples / constants.randomise(this.processingSpeed)