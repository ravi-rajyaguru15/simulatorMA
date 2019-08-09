import sim.constants
from sim.result import result 

class server:
	message = None
	processingSpeed = sim.constants.SERVER_PROCESSING_SPEED
	messageOverheadLatency = sim.constants.SERVER_MESSAGE_OVERHEAD_LATENCY
	transmissionRate = sim.constants.ETHERNET_SPEED
	transmissionPing = sim.constants.ETHERNET_PING

	def process(this):
		res = result(latency=this.processingTime(this.message.samples), energy=0)

		this.message.process()

		return res

	def processingTime(this, samples):
		return samples / this.processingSpeed.gen()

	def sendTo(this, destination):
		latency = this.messageOverheadLatency.gen() + this.txLatency(this.message.size)

		reception = destination.receive(this.message)
		this.message = None

		return reception + result(latency, 0)

	def receive(this, message):
		this.message = message;
		# reception does not add energy or latency
		return result()

	def txLatency(this, messageSize):
		return messageSize / 1024. / this.transmissionRate.gen() + this.transmissionPing.gen()