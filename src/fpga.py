from result import result
import constants 

class fpga:
	internalVoltage = constants.FPGA_INT_VOLTAGE
	auxVoltage = constants.FPGA_AUX_VOLTAGE

	activeInternalCurrent = constants.FPGA_ACTIVE_INT_CURRENT
	idleInternalCurrent = constants.FPG_IDLE_INT_CURRENT
	activeAuxCurrent = constants.FPGA_ACTIVE_AUX_CURRENT
	idleAuxCurrent = constants.FPG_IDLE_AUX_CURRENT

	processingSpeed = constants.FPGA_PROCESSING_SPEED

	def __init__(this):
		# this.internalVoltage = internalVoltage
		# this.auxVoltage = auxVoltage
		pass

	def processingLatency(this, samples):
		return samples / constants.randomise(this.processingSpeed)

	def process(this, samples):
		res = result(latency=this.processingLatency(samples), energy=this.activeEnergy(this.processingLatency(samples)))
		return res

	def activeEnergy(this, duration):
		return duration * (constants.randomise(this.internalVoltage) * constants.randomise(this.activeInternalCurrent) + constants.randomise(this.auxVoltage) + constants.randomise(this.activeAuxCurrent))