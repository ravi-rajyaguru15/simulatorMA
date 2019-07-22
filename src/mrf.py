import constants 
import random

class mrf:
	voltage = constants.MCU_VOLTAGE
	rxCurrent, txCurrent = constants.WIRELESS_RX_CURRENT, constants.WIRELESS_TX_CURRENT
	transmissionRate = constants.WIRELESS_SPEED

	# def __init__(this, txCurrent=None, rxCurrent = None):

	# 	if txCurrent is None:
	# 		this.txCurrent = constants.WIRELESS_CURRENT)
	# 	else:
	# 		this.txCurrent = txCurrent


	# 	if rxCurrent is None:
	# 		this.rxCurrent = constants.WIRELESS_CURRENT)
	# 	else:
	# 		this.rxCurrent = rxCurrent

	def txEnergy(this, messageSize):
		return messageSize / 1024. / this.transmissionRate.gen() * this.voltage.gen() * this.txCurrent.gen() / 1000.

	def rxEnergy(this, messageSize):
		return messageSize / 1024. / this.transmissionRate.gen() * this.voltage.gen() * this.rxCurrent.gen() / 1000.

	def rxtxLatency(this, messageSize):
		# print 'size', messageSize, 'lat', messageSize / 1024. / this.transmissionRate)
		return messageSize / 1024. / this.transmissionRate.gen()