from endDevice import endDevice
from elasticNode import elasticNode
# from message import message
from result import result
from gateway import gateway
from server import server
from visualiser import visualiser 

import constants
import variable

import multiprocessing
import sys
import numpy as np

class sim:
	ed, ed2, en, gw, srv, selectedOptions = None, None, None, None, None, None
	results = None
	time = None
	devices = None
	visualise = None
	visualisor = None
	finished = False
	hardwareAccelerated = None

	def __init__(self, numEndDevices, numElasticNodes, numServers, visualise=False, hardwareAccelerated=None):
		print (numEndDevices, numElasticNodes)
		self.results = multiprocessing.Manager().Queue()
		index = 0

		self.time = 0
		
		self.ed = [endDevice(self.results, i, alwaysHardwareAccelerate=hardwareAccelerated) for i in range(numEndDevices)]
		# self.ed = endDevice()
		# self.ed2 = endDevice()
		self.en = [elasticNode(self.results, i + numEndDevices, alwaysHardwareAccelerate=hardwareAccelerated) for i in range(numElasticNodes)]
		# self.en = elasticNode()
		self.gw = gateway()
		self.srv = [server() for i in range(numServers)]

		self.devices = self.ed + self.en + self.srv
		# set all device options correctly
		print (constants.OFFLOADING_POLICY)
		for device in self.devices: 
			# choose options based on policy
			if constants.OFFLOADING_POLICY == constants.LOCAL_ONLY:
				device.setOffloadingDecisions([device])
			elif constants.OFFLOADING_POLICY == constants.PEER_ONLY:
				tmpList = list(self.en)
				tmpList.remove(device)
				device.setOffloadingDecisions(tmpList)

		self.hardwareAccelerated = hardwareAccelerated
		self.visualise = visualise
		if self.visualise:
			self.visualiser = visualiser(self)

	def stop(self):
		print ("STOP")
		self.finished = True

	def simulateTime(self, duration):
		progress = 0
		queueLengths = list()
		plotFrames = constants.PLOT_TD / constants.TD
		print (plotFrames)
		frames = 0

		while progress < duration and not self.finished:
			# try:
			if True:
				frames += 1

				# create new jobs
				for device in self.devices:
					if not device.busy():
						device.maybeAddNewJob()
					
				# update all the devices
				for dev in self.devices:
					dev.updateTime()
					queueLengths.append(len(dev.jobQueue))
				
				print ("jobQueues:", [len(dev.jobQueue) for dev in self.devices])
				print ("busy:", [dev.busy() for dev in self.devices])
				print ("tasks", [dev.currentTask for dev in self.devices])

				progress += constants.TD

				if self.visualise:
					if frames % plotFrames == 0:
						self.visualiser.update()
			# except:
			# 	print "fail"
			# 	self.finished = True

		try:
			latencies = list()
			energies = list()
			for i in range(self.results.qsize()):
				value = self.results.get()
				
				samples = value[0]
				res = value[1]

				latencies.append(res.latency)
				energies.append(res.energy)
			
			queueLengths = np.array(queueLengths)
			print ("averages:")
			print ("latency:\t", 	np.average(np.array(latencies)))
			print ("energy:\t\t", 	np.average(np.array(energies)))
			print ("jobs:\t\t", 		np.average(queueLengths))
			print (np.histogram(queueLengths, bins=np.array(range(np.max(queueLengths) + 3)) - .5))
		except:
			print ("no results available")

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
	
	@staticmethod
	def singleDelayedJobLocal(accelerated=True):
		constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
		
		simulation = sim(0, 2, 0, visualise=True)

		constants.JOB_LIKELIHOOD = 0
		# simulation.en[0].createNewJob()
		# simulation.simulateTime(constants.SIM_TIME)
		simulation.simulateTime(constants.PLOT_TD * 10)
		simulation.devices[0].createNewJob(hardwareAccelerated=accelerated)
		simulation.simulateTime(0.25)
		
	@staticmethod
	def singleDelayedJobPeer(accelerated=True):
		constants.OFFLOADING_POLICY = constants.PEER_ONLY
		
		simulation = sim(0, 2, 0, visualise=True)

		constants.JOB_LIKELIHOOD = 0
		simulation.simulateTime(constants.PLOT_TD * 10)
		simulation.devices[0].createNewJob(hardwareAccelerated=accelerated)
		simulation.simulateTime(constants.PLOT_TD * 150)
		
	@staticmethod
	def randomPeerJobs(accelerated=True):
		constants.OFFLOADING_POLICY = constants.PEER_ONLY
		
		simulation = sim(0, 4, 0, visualise=True, hardwareAccelerated=accelerated)

		constants.JOB_LIKELIHOOD = 5e-2
		simulation.simulateTime(constants.PLOT_TD * 100)
		
	@staticmethod
	def randomLocalJobs(accelerated=True):
		constants.SAMPLE_SIZE = variable.Uniform(5,6)
		constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
		
		simulation = sim(0, 2, 0, visualise=True)

		constants.JOB_LIKELIHOOD = 5e-2
		simulation.simulateTime(constants.PLOT_TD * 100)
		

if __name__ == '__main__':
	# for i in range(1, 100, 10):
	# 	print i, simulation.simulateAll(i, "latency")

	# sim.singleDelayedJobLocal(True)
	sim.singleDelayedJobPeer(True)
	# sim.randomPeerJobs(True)
	# sim.randomPeerJobs(False)