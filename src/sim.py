from endDevice import endDevice
from elasticNode import elasticNode
from message import message
from result import result
from gateway import gateway
from server import server

class sim:
	ed, ed2, en, gw, srv = None, None, None, None, None

	def __init__(self):
		self.ed = endDevice()
		self.ed2 = endDevice()
		self.en = elasticNode()
		self.gw = gateway()
		self.srv = server()

	def offloadElasticNode(self, samples):
		self.ed.message = message(samples=samples)

		# offload to elastic node
		res = self.ed.sendTo(self.en)
		res += self.en.process(accelerated=True)
		res += self.en.sendTo(self.ed)
		# print 'offload elastic node:\t', res

		return res

	def localProcess(self, samples):
		# process locally
		self.ed.message = message(samples=samples)
		res = self.ed.process() 
		# print 'local:\t\t\t\t\t', res

		return res

	def offloadPeer(self, samples):
		# offload to neighbour
		self.ed.message = message(samples=samples)
		res = self.ed.sendTo(self.ed2)
		# print res
		res += self.ed2.process()
		# print res
		res += self.ed2.sendTo(self.ed)
		# print res
		# print 'offload p2p:\t\t\t', res

		return res

	def offloadServer(self, samples):

		# offload to server
		self.ed.message = message(samples=samples)
		res = self.ed.sendTo(self.gw)
		res += self.gw.sendTo(self.srv)
		res += self.srv.process()
		res += self.srv.sendTo(self.gw)
		res += self.gw.sendTo(self.ed)
		# print 'offload server:\t\t\t', res

		return res

	def simulateBatch(self, batch, attribute, queue):
		for samples in batch:
			# print 'samples', samples
			self.simulateAll(samples, attribute, queue)

	options = [offloadElasticNode, localProcess, offloadPeer, offloadServer]
	optionsNames = ["offloadElasticNode", "localProcess", "offloadPeer", "offloadServer"]
	# simulate all available options, and output the chosen attribute
	def simulateAll(self, samples, attribute, queue=None):
		outputs = list()
		for processing in self.options:
			outputs.append(processing(self, samples).__dict__[attribute])
			# queue.put(processing(self, samples).__dict__[attribute])
		# return outputs
		if queue is not None:
			queue.put([samples, outputs])
		else:
			return outputs
		#print samples
		#print outputs

	def numOptions(self):
		return len(self.options)

	def nameOptions(self):
		return self.optionsNames

if __name__ == '__main__':
	simulation = sim()
	for i in range(1, 100, 10):
		print (i, simulation.simulateAll(i, "latency"))
