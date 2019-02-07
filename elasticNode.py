import constants
from mcu import mcu
from mrf import mrf
from fpga import fpga
from result import result

class elasticNode:
	message = None
	mcu = None
	mrf = None
	fpga = None

	def __init__(this):
		this.mcu = mcu()
		this.mrf = mrf()
		this.fpga = fpga()

	def sendTo(this, destination):
		latency = constants.randomise(this.mcu.messageOverheadLatency) + this.mrf.rxtxLatency(this.message.size)
		energy = this.mcu.overheadEnergy() + this.mrf.txEnergy(this.message.size)

		res = destination.receive(this.message)
		this.message = None

		return result(latency, energy) + res

	def receive(this, message):
		this.message = message;
		# reception does not add latency
		return result(latency=0, energy=this.mcu.activeEnergy(this.mrf.rxtxLatency(this.message.size) + this.mrf.rxEnergy(this.message.size)))

	def mcuToFpgaLatency(this):
		return this.message.size / 1024./ constants.randomise(constants.MCU_FPGA_COMMUNICATION_SPEED)

	def mcuToFpgaEnergy(this):
		mcuEnergy = this.mcu.activeEnergy(this.mcuToFpgaLatency())
		fpgaEnergy = this.fpga.activeEnergy(this.mcuToFpgaLatency())
		return mcuEnergy + fpgaEnergy

	def process(this, accelerated):
		res = None
		if accelerated:
			# overhead for mcu-fpga communication
			res = result(latency=this.mcuToFpgaLatency(), energy=this.mcuToFpgaEnergy())
			# processing 
			res += this.fpga.process(this.message.samples)
		else:
			res = result(latency=this.mcu.processingTime(this.message.samples), energy=this.mcu.activeEnergy(this.mcu.processingTime(this.message.samples)))

		this.message.process()

		return res
