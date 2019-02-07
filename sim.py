from endDevice import endDevice
from elasticNode import elasticNode
from message import message
from result import result
from gateway import gateway
from server import server

class sim:
	ed, ed2, en, gw, srv = None, None, None, None, None

	def __init__(this):
		this.ed = endDevice()
		this.ed2 = endDevice()
		this.en = elasticNode()
		this.gw = gateway()
		this.srv = server()

	def offloadElasticNode(this, samples):
		this.ed.message = message(samples=samples)

		# offload to elastic node
		res = this.ed.sendTo(this.en)
		res += this.en.process(accelerated=True)
		res += this.en.sendTo(this.ed)
		# print 'offload elastic node:\t', res

		return res

	def localProcess(this, samples):
		# process locally
		this.ed.message = message(samples=samples)
		res = this.ed.process() 
		# print 'local:\t\t\t\t\t', res

		return res

	def offloadPeer(this, samples):
		# offload to neighbour
		this.ed.message = message(samples=samples)
		res = this.ed.sendTo(this.ed2)
		res += this.ed2.process()
		# print 'offload p2p:\t\t\t', res

		return res

	def offloadServer(this, samples):

		# offload to server
		this.ed.message = message(samples=samples)
		res = this.ed.sendTo(this.gw)
		res += this.gw.sendTo(this.srv)
		res += this.srv.process()
		res += this.srv.sendTo(this.gw)
		res += this.gw.sendTo(this.ed)
		# print 'offload server:\t\t\t', res

		return res

	options = [offloadElasticNode, localProcess, offloadPeer, offloadServer]
	optionsNames = ["offloadElasticNode", "localProcess", "offloadPeer", "offloadServer"]
	# simulate all available options, and output the chosen attribute
	def simulateAll(this, samples, attribute):
		outputs = list()
		for processing in this.options:
			outputs.append(processing(this, samples).__dict__[attribute])
		
		return outputs

	def numOptions(this):
		return len(this.options)

	def nameOptions(this):
		return this.optionsNames

if __name__ == '__main__':
	simulation = sim()
	simulation.offloadElasticNode(100)
	simulation.localProcess(100)
	simulation.offloadPeer(100)
	simulation.offloadServer(100)