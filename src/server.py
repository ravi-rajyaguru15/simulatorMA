import constants
from result import result 

class server:
	message = None
	processingSpeed = constants.SERVER_PROCESSING_SPEED
	messageOverheadLatency = constants.SERVER_MESSAGE_OVERHEAD_LATENCY
	transmissionRate = constants.ETHERNET_SPEED
	transmissionPing = constants.ETHERNET_PING

	def process(this):
		res = result(latency=this.processingTime(this.message.samples), energy=0)

		this.message.process()

		return res

	def processingTime(this, samples):
		return samples / constants.randomise(this.processingSpeed)

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