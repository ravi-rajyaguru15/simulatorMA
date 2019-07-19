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
		return this.messageOverheadLatency.gen() * this.activeCurrent.gen() / 1000. * this.voltage.gen()

	def activeEnergy(this, time):
		return time * this.voltage.gen() * this.activeCurrent.gen()

	def processingTime(this, samples):
		return samples / this.processingSpeed.gen()