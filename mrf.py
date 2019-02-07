import constants 
import random

class mrf:
	voltage = constants.MCU_VOLTAGE
	rxCurrent, txCurrent = constants.WIRELESS_RX_CURRENT, constants.WIRELESS_TX_CURRENT
	transmissionRate = constants.WIRELESS_SPEED

	# def __init__(this, txCurrent=None, rxCurrent = None):

	# 	if txCurrent is None:
	# 		this.txCurrent = constants.randomise(constants.WIRELESS_CURRENT)
	# 	else:
	# 		this.txCurrent = txCurrent


	# 	if rxCurrent is None:
	# 		this.rxCurrent = constants.randomise(constants.WIRELESS_CURRENT)
	# 	else:
	# 		this.rxCurrent = rxCurrent

	def txEnergy(this, messageSize):
		return messageSize / 1024. / constants.randomise(this.transmissionRate) * constants.randomise(this.voltage) * constants.randomise(this.txCurrent) / 1000.

	def rxEnergy(this, messageSize):
		return messageSize / 1024. / constants.randomise(this.transmissionRate) * constants.randomise(this.voltage) * constants.randomise(this.rxCurrent) / 1000.

	def rxtxLatency(this, messageSize):
		return messageSize / 1024. / constants.randomise(this.transmissionRate)