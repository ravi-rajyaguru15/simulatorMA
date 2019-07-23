import constants 
import random

class mrf:
	voltage = constants.MCU_VOLTAGE
	rxCurrent, txCurrent = constants.WIRELESS_RX_CURRENT, constants.WIRELESS_TX_CURRENT
	transmissionRate = constants.WIRELESS_SPEED

	busy = None

	def __init__(self):
		self.busy = False

	# def __init__(self, txCurrent=None, rxCurrent = None):

	# 	if txCurrent is None:
	# 		self.txCurrent = constants.WIRELESS_CURRENT)
	# 	else:
	# 		self.txCurrent = txCurrent


	# 	if rxCurrent is None:
	# 		self.rxCurrent = constants.WIRELESS_CURRENT)
	# 	else:
	# 		self.rxCurrent = rxCurrent

	def txEnergy(self, duration):
		return duration * self.voltage.gen() * self.txCurrent.gen() / 1000.

	def rxEnergy(self, duration):
		return duration * self.voltage.gen() * self.rxCurrent.gen() / 1000.

	def rxtxLatency(self, messageSize):
		# print 'size', messageSize, 'lat', messageSize / 1024. / self.transmissionRate)
		return messageSize / 1024. / self.transmissionRate.gen()