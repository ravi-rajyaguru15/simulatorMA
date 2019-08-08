from endDevice import endDevice
from elasticNode import elasticNode
# from message import message
from result import result
from gateway import gateway
from server import server
from visualiser import visualiser 
from job import job
import debug

import constants
import variable
import tasks

import multiprocessing
import sys
import numpy as np

class sim:
	ed, ed2, en, gw, srv, selectedOptions = None, None, None, None, None, None
	results = None
	jobResults = None
	time = None
	devices = None
	visualise = None
	visualisor = None
	finished = False
	hardwareAccelerated = None

	def __init__(self, numEndDevices, numElasticNodes, numServers, visualise=False, hardwareAccelerated=None):
		debug.out(numEndDevices + numElasticNodes)
		self.results = multiprocessing.Manager().Queue()
		self.jobResults = multiprocessing.Manager().Queue()
		job.jobResultsQueue = self.jobResults
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
		# print (constants.OFFLOADING_POLICY)
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
		debug.out("STOP", 'r')
		self.finished = True

	def allDone(self):
		return np.all([not device.hasJob() for device in self.devices])
	
	# def simulateUntilDone()
	
	def simulateTime(self, duration):
		# progress = 0
		endTime = self.time + duration
		queueLengths = list()
		plotFrames = constants.PLOT_TD / constants.TD
		debug.out (plotFrames)
		frames = 0

		while self.time < endTime and not self.finished:
			# try:
			if True:
				debug.out('tick', 'b')
				frames += 1

				# create new jobs
				for device in self.devices:
					if not device.hasJob():
						device.maybeAddNewJob()
					
				debug.out("tasks before {0}".format([dev.currentTask for dev in self.devices]), 'r')

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


				
				debug.out("jobQueues:\t\t{0}".format([len(dev.jobQueue) for dev in self.devices]), 'g')
				debug.out("taskQueues:\t{0}".format([len(dev.taskQueue) for dev in self.devices]), 'dg')
				debug.out("have jobs: {0}".format([dev.hasJob() for dev in self.devices]))
				debug.out("states: {0}".format([[comp.state for comp in dev.components] for dev in self.devices]))
				debug.out("tasks after {0}".format([dev.currentTask for dev in self.devices]), 'r')

				# progress += constants.TD
				self.time += constants.TD

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
			debug.out("averages:")
			# debug.out ("latency:\t", 	np.average(np.array(latencies)))
			# debug.out ("energy:\t\t", 	np.average(np.array(energies)))
			# debug.out ("jobs:\t\t", 		np.average(queueLengths))
			debug.out (np.histogram(queueLengths, bins=np.array(range(np.max(queueLengths) + 3)) - .5))
		except:
			debug.out ("no results available")

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
	# for i in range(1, 100, 10):
	# 	print i, simulation.simulateAll(i, "latency")

	# sim.singleDelayedJobLocal(False)
	sim.singleDelayedJobLocal(True)
	# sim.singleDelayedJobPeer(False)
	# sim.singleDelayedJobPeer(True)
	# sim.randomPeerJobs(True)
	# sim.randomPeerJobs(False)
	# sim.singleBatchLocal(False)
