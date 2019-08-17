from sim.endDevice import endDevice
from sim.elasticNode import elasticNode
# from message import message
from sim.result import result
from sim.gateway import gateway
from sim.server import server
from sim.visualiser import visualiser 
from sim.job import job
import sim.debug

import sim.constants
import sim.variable
import sim.tasks

import multiprocessing
import sys
import numpy as np

queueLengths = list()

class simulation:
	ed, ed2, en, gw, srv, selectedOptions = None, None, None, None, None, None
	results = None
	jobResults = None
	time = None
	devices = None
	delays = None
	currentDelays = None
	# visualise = None
	visualisor = None
	finished = False
	hardwareAccelerated = None

	def __init__(self, numEndDevices, numElasticNodes, numServers, hardwareAccelerated=None):
		sim.debug.out(numEndDevices + numElasticNodes)
		self.results = multiprocessing.Manager().Queue()
		self.jobResults = multiprocessing.Manager().Queue()
		job.jobResultsQueue = self.jobResults
		self.delays = list()

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
		# print (sim.constants.OFFLOADING_POLICY)
		for device in self.devices: 
			# choose options based on policy
			device.setOffloadingDecisions(self.devices)

		self.hardwareAccelerated = hardwareAccelerated
		# self.visualise = visualise
		if sim.constants.DRAW:
			self.visualiser = visualiser(self)

	def stop(self):
		sim.debug.out("STOP", 'r')
		self.finished = True

	def allDone(self):
		return np.all([not device.hasJob() for device in self.devices])
	
	def simulate(self):
		frames = 0
		plotFrames = sim.constants.PLOT_TD / sim.constants.TD

		while not self.finished:
			frames += 1
			self.simulateTick()
			
			if sim.constants.DRAW or sim.constants.SAVE:
				if frames % plotFrames == 0:
					self.visualiser.update()
		
			# pass
				# def simulateUntilDone()
	
	def simulateUntilTime(self, finalTime):
		assert(finalTime > self.time)
		self.simulateTime(finalTime - self.time)

	def simulateTime(self, duration):
		# progress = 0
		endTime = self.time + duration
		plotFrames = sim.constants.PLOT_TD / sim.constants.TD
		sim.debug.out (plotFrames)
		frames = 0

		while self.time < endTime and not self.finished:
			# try:
			if True:
				self.simulateTick()
				frames += 1

				if sim.constants.DRAW:
					if frames % plotFrames == 0:
						self.visualiser.update()
		
		# results
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
			sim.debug.out("averages:")
			# sim.debug.out ("latency:\t", 	np.average(np.array(latencies)))
			# sim.debug.out ("energy:\t\t", 	np.average(np.array(energies)))
			# sim.debug.out ("jobs:\t\t", 		np.average(queueLengths))
			sim.debug.out (np.histogram(queueLengths, bins=np.array(range(np.max(queueLengths) + 3)) - .5))
		except:
			sim.debug.out ("no results available")		


	def simulateTick(self):
		try:
			sim.debug.out('tick {:.4f}'.format(self.time), 'b')

			# create new jobs
			for device in self.devices:
				# mcu is required for taking samples
				if not device.hasJob():
					device.maybeAddNewJob(self.time)
				
			sim.debug.out("tasks before {0}".format([dev.currentTask for dev in self.devices]), 'r')

			# update all the devices
			for dev in self.devices:
				dev.updateTime(self.time)
				queueLengths.append(len(dev.jobQueue))

			# capture energy values
			for dev in self.devices:
				energy = dev.energy()

				# add energy to device counter
				dev.totalEnergyCost += energy
				# add energy to job 
				if dev.currentJob is not None:
					dev.currentJob.totalEnergyCost += energy
					# see if device is in job history
					if dev not in dev.currentJob.devicesEnergyCost.keys():
						dev.currentJob.devicesEnergyCost[dev] = 0
					
					dev.currentJob.devicesEnergyCost[dev] += energy



			sim.debug.out("have jobs:\t{0}".format([dev.hasJob() for dev in self.devices]), 'b')
			sim.debug.out("jobQueues:\t{0}".format([len(dev.jobQueue) for dev in self.devices]), 'g')
			sim.debug.out("batch:\t\t{0}".format([len(dev.batch) for dev in self.devices]), 'c')
			sim.debug.out("taskQueues:\t{0}".format([len(dev.taskQueue) for dev in self.devices]), 'dg')
			sim.debug.out("taskQueues:\t{0}".format([dev.taskQueue for dev in self.devices]), 'dg')
			sim.debug.out("states: {0}".format([[comp.state for comp in dev.components] for dev in self.devices]))
			sim.debug.out("tasks after {0}".format([dev.currentTask for dev in self.devices]), 'r')
			
			self.currentDelays = [dev.currentTask.delay if dev.currentTask is not None else 0 for dev in self.devices ]
			self.delays.append(self.currentDelays)
			if np.sum(self.currentDelays) > 0:
				sim.debug.out("delays {}".format(self.currentDelays))
			# progress += sim.constants.TD
			self.time += sim.constants.TD
		except Exception:
			print ("Exception", self.time)
			raise Exception("crash")

			# except:
			# 	print "fail"
			# 	self.finished = True

	

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

	# def numOptions(self):
	# 	return len(self.options)

	# def nameOptions(self):
	# 	return self.optionsNames

	def devicesNames(self):
		return [dev for dev in self.devices]

	def totalDevicesEnergy(self):
		return [dev.totalEnergyCost for dev in self.devices]

	def currentDevicesEnergy(self):
		return [dev.energy() for dev in self.devices]

	def numSelectedOptions(self):
		if self.selectedOptions is None:
			return self.numOptions()
		else:
			return len(self.selectedOptions)

	def selectedNameOptions(self):
		return [self.optionsNames[option] for option in self.selectedOptions]
	

if __name__ == '__main__':
	print ("running sim")

	# for i in range(1, 100, 10):
	# 	print i, simulation.simulateAll(i, "latency")

	# simulation.singleDelayedJobLocal(False)
	# simulation.singleDelayedJobLocal(True)
	# simulation.singleDelayedJobPeer(False)
	# simulation.singleDelayedJobPeer(True)
	# simulation.randomPeerJobs(True)
	simulation.randomPeerJobs(False)
	# simulation.singleBatchLocal(False)
