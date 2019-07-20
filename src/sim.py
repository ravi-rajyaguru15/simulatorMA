from endDevice import endDevice
from elasticNode import elasticNode
from message import message
from result import result
from gateway import gateway
from server import server

import constants

import multiprocessing
import sys
import numpy as np

class sim:
	ed, ed2, en, gw, srv, selectedOptions = None, None, None, None, None, None
	results = None
	time = None

	def __init__(self, numEndDevices, numElasticNodes, numServers):
		print numEndDevices, numElasticNodes
		self.results = multiprocessing.Manager().Queue()

		self.time = 0
		
		self.ed = [endDevice(self.results) for i in range(numEndDevices)]
		# self.ed = endDevice()
		# self.ed2 = endDevice()
		self.en = [elasticNode(self.results) for i in range(numElasticNodes)]
		# self.en = elasticNode()
		self.gw = gateway()
		self.srv = [server() for i in range(numServers)]

		devices = self.ed + self.en + self.srv
		for device in devices: 
			device.setOffloadingDecisions(devices)


	def simulateTime(self, duration):
		progress = 0
		queueLengths = list()
		while progress < duration:
			# update all the devices
			for en in self.en:
				en.updateTime()
				queueLengths.append(len(en.jobQueue))

			progress += constants.TD

		latencies = list()
		energies = list()
		for i in range(self.results.qsize()):
			value = self.results.get()
			
			samples = value[0]
			res = value[1]

			latencies.append(res.latency)
			energies.append(res.energy)

		queueLengths = np.array(queueLengths)
		print "averages:"
		print "latency:\t", 	np.average(np.array(latencies))
		print "energy:\t\t", 	np.average(np.array(energies))
		print "jobs:\t\t", 		np.average(queueLengths)
		print np.histogram(queueLengths, bins=range(np.max(queueLengths) + 3)) 
	# def simulateBatch(self, batch, attribute):
	# 	for samples in batch:
	# 		# print 'samples', samples
	# 		self.simulateAll(samples, attribute)

	# options = [offloadElasticNode, localProcessMcu, localProcessFpga, offloadPeer, offloadServer]
	# optionsNames = ["offloadElasticNode", "localProcessMcu", "localProcessFpga", "offloadPeer", "offloadServer"]
	# # simulate all available options, and output the chosen attribute
	# def simulateAll(self, samples, attribute):
	# 	# if no options selected, select all
	# 	if self.selectedOptions is None: 
	# 		# print "Selecting all available options"
	# 		self.selectedOptions = range(self.numOptions())

	# 	outputs = list()
	# 	for processing in [self.options[option] for option in self.selectedOptions]:
	# 		outputs.append(processing(self, samples).__dict__[attribute])
	# 		# queue.put(processing(self, samples).__dict__[attribute])

	# 	if self.queue is not None:
	# 		self.queue.put([samples, outputs])
	# 	else:
	# 		return outputs

	def numOptions(self):
		return len(self.options)

	def nameOptions(self):
		return self.optionsNames

	def numSelectedOptions(self):
		if self.selectedOptions is None:
			return self.numOptions()
		else:
			return len(self.selectedOptions)

	def selectedNameOptions(self):
		return [self.optionsNames[option] for option in self.selectedOptions]

if __name__ == '__main__':
	simulation = sim(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
	# for i in range(1, 100, 10):
	# 	print i, simulation.simulateAll(i, "latency")

	simulation.simulateTime(constants.SIM_TIME)
	