from sim.simulations.result import result

class gateway:
	message = None
	transmissionRate = None
	transmissionPing = None
	messageOverheadLatency = None

	def __init__(self, platform):
		self.transmissionRate = platform.ETHERNET_SPEED
		self.transmissionPing = platform.ETHERNET_PING
		self.messageOverheadLatency = platform.SERVER_MESSAGE_OVERHEAD_LATENCY

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