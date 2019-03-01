import constants
from result import result

class gateway:
	message = None
	transmissionRate = constants.ETHERNET_SPEED
	transmissionPing = constants.ETHERNET_PING
	messageOverheadLatency = constants.SERVER_MESSAGE_OVERHEAD_LATENCY

	def sendTo(this, destination):
		latency = constants.randomise(this.messageOverheadLatency) + this.txLatency(this.message.size)

		reception = destination.receive(this.message)
		this.message = None

		return reception + result(latency, 0)

	def receive(this, message):
		this.message = message;
		# reception does not add energy or latency
		return result()

	def txLatency(this, messageSize):
		return messageSize / 1024. / constants.randomise(this.transmissionRate) + constants.randomise(this.transmissionPing)