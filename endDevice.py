import random
import constants

from mcu import mcu
from mrf import mrf
from result import result

class endDevice:
	message = None

	def __init__(this):
		this.mcu = mcu()
		this.mrf = mrf()

	def sendTo(this, destination):
		latency = constants.randomise(this.mcu.messageOverheadLatency) + this.mrf.rxtxLatency(this.message.size)
		energy = this.mcu.overheadEnergy() + this.mcu.activeEnergy(this.mrf.rxtxLatency(this.message.size)) + this.mrf.txEnergy(this.message.size)

		reception = destination.receive(this.message)
		this.message = None

		return result(latency, energy) + reception


	def receive(this, message):
		this.message = message;
		# reception does not add latency
		return result(latency=0, energy=this.mcu.activeEnergy(this.mrf.rxtxLatency(this.message.size) + this.mrf.rxEnergy(this.message.size)))

	def process(this):
		time = this.mcu.processingTime(this.message.samples)
		res = result(latency=time, energy=this.mcu.activeEnergy(time))

		this.message.process()

		return res
