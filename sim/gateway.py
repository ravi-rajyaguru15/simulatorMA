import sim.constants
from sim.result import result

class gateway:
	message = None
	transmissionRate = sim.constants.ETHERNET_SPEED
	transmissionPing = sim.constants.ETHERNET_PING
	messageOverheadLatency = sim.constants.SERVER_MESSAGE_OVERHEAD_LATENCY

	def sendTo(self, destination):
		latency = self.messageOverheadLatency.gen() + self.txLatency(self.message.size)

		reception = destination.receive(self.message)
		self.message = None

		return reception + result(latency, 0)

	def receive(self, message):
		self.message = message
		# reception does not add energy or latency
		return result()

	def txLatency(self, messageSize):
		return messageSize / 1024. / self.transmissionRate.gen() + self.transmissionPing.gen()