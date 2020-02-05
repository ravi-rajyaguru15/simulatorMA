from queue import PriorityQueue

from sim.simulations.Simulation import queueLengths, BasicSimulation
from sim import constants, debug, offloadingPolicy, offloadingDecision, systemState
from sim.elasticNode import elasticNode
import numpy as np

from sim.subtask import subtask


class SimpleSimulation(BasicSimulation):
	queue = None

	def __init__(self, hardwareAccelerated=True):
		BasicSimulation.__init__(self, hardwareAccelerated=hardwareAccelerated)
		# specify subtask behaviour
		subtask.update = subtask.perform

		self.queue = PriorityQueue()

		# need to initially check when each device's first task is
		for dev in self.devices:
			self.queueNextJob(dev)

	def simulateTick(self):
		# try:
		if constants.OFFLOADING_POLICY == offloadingPolicy.REINFORCEMENT_LEARNING:
			systemState.current.updateSystem()

		# # create new jobs
		# for device in self.devices:
		# 	# mcu is required for taking samples
		# 	if not device.hasJob():
		# 		device.maybeAddNewJob()
		#
		# 	# force updating td
		# 	device.currentTd = None

		# update the destination of the offloading if it is shared
		if constants.OFFLOADING_POLICY == offloadingPolicy.ROUND_ROBIN:
			offloadingDecision.updateOffloadingTarget()

		tasksBefore = np.array([dev.currentSubtask for dev in self.devices])

		# process new queued task here
		# newTime, arguments = self.queue.get()
		nextTask = self.queue.get()
		newTime = nextTask.priority
		arguments = nextTask.item
		print("new time", newTime, arguments)
		self.time.set(newTime)
		self.processQueuedTask(arguments)

		# # update all the devices
		# for dev in self.devices:
		# 	if not (dev.currentJob is None and dev.currentSubtask is None):
		# 		debug.out('\ntick device [{}] [{}] [{}]'.format(dev, dev.currentJob, dev.currentSubtask))
		# 	dev.updateTime(self.time)
		# 	queueLengths.append(len(dev.jobQueue))

		# # capture energy values
		# for dev in self.devices:
		# 	energy = dev.energy()
		#
		# 	# # add energy to device counter
		# 	# dev.totalEnergyCost += energy
		# 	# add energy to job
		# 	if dev.currentJob is not None:
		# 		dev.currentJob.totalEnergyCost += energy
		# 		# see if device is in job history
		# 		if dev not in dev.currentJob.devicesEnergyCost.keys():
		# 			dev.currentJob.devicesEnergyCost[dev] = 0
		#
		# 		dev.currentJob.devicesEnergyCost[dev] += energy

		if constants.DRAW_GRAPH_EXPECTED_LIFETIME:
			# note energy levels for plotting
			self.timestamps.append(self.time)
			self.lifetimes.append(self.devicesLifetimes())
			self.energylevels.append(self.devicesEnergyLevels())

		self.finished = self.systemLifetime() <= 0

		# check if task queue is too long
		self.taskQueueLength = [len(dev.taskQueue) for dev in self.devices]
		# for i in range(len(self.devices)):
		# 	if self.taskQueueLength[i] > constants.MAXIMUM_TASK_QUEUE:
		# 		# check distribution of job assignments
		# 		unique, counts = np.unique(np.array(results.chosenDestinations[:-1]), return_counts=True)
		# 		print(dict(zip(unique, counts)))

		# 		warnings.warn("TaskQueue for {} too long! {} Likelihood: {}".format(self.devices[i], len(self.devices[i].taskQueue), constants.JOB_LIKELIHOOD))

		self.currentDelays = [dev.currentSubtask.delay if dev.currentSubtask is not None else 0 for dev in self.devices]
		self.delays.append(self.currentDelays)

		# print all results if interesting
		tasksAfter = np.array([dev.currentSubtask for dev in self.devices])
		# if debug.enabled:
		# 	if not (np.all(tasksAfter == None) and np.all(tasksBefore == None)):
		# 		debug.out('tick {}'.format(self.time), 'b')
		# 		# 	debug.out("nothing...")
		# 		# else:
		# 		debug.out("tasks before {0}".format(tasksBefore), 'r')
		# 		debug.out("have jobs:\t{0}".format([dev.hasJob() for dev in self.devices]), 'b')
		# 		debug.out("jobQueues:\t{0}".format([len(dev.jobQueue) for dev in self.devices]), 'g')
		# 		debug.out("batchLengths:\t{0}".format(self.batchLengths()), 'c')
		# 		debug.out("currentBatch:\t{0}".format([dev.currentBatch for dev in self.devices]))
		# 		debug.out("currentConfig:\t{0}".format([dev.fpga.currentConfig for dev in self.devices if isinstance(dev, elasticNode)]))
		# 		debug.out("taskQueues:\t{0}".format([len(dev.taskQueue) for dev in self.devices]), 'dg')
		# 		debug.out("taskQueues:\t{0}".format([[task for task in dev.taskQueue] for dev in self.devices]), 'dg')
		# 		debug.out("states: {0}".format([[comp.state for comp in dev.components] for dev in self.devices]))
		# 		debug.out("tasks after {0}".format(tasksAfter), 'r')
		#
		# 		if np.sum(self.currentDelays) > 0:
		# 			debug.out("delays {}".format(self.currentDelays))

		self.frames += 1
		# if constants.DRAW_DEVICES:
		if self.frames % self.plotFrames == 0:
			self.visualiser.update()

		# progress += constants.TD

	# add next job to be created for this device to backlog
	def queueNextJob(self, device):
		assert device is not None

		# next job in:
		nextInterval = constants.JOB_INTERVAL.gen()
		nextJob = self.time + nextInterval

		print("next job is at", nextJob, device)
		# add task to queue
		self.queue.put(PrioritizedItem(nextJob, (NEW_JOB, device)))
		device.futureJob = True

	# do next queued task
	def processQueuedTask(self, args):
		task = args[0]
		if task == NEW_JOB:
			print("creating new job")
			device = args[1]
			self.createNewJob(device)
			device.futureJob = False

			# immediately start created job
			affectedDevice = device.nextJob()
			print("pre affected", affectedDevice)
			# start created subtask
			self.processDeviceSubtask(affectedDevice)
		elif task == CONTINUE_JOB:
			print("continue existing job")
			device = args[1]
			self.processDeviceSubtask(device)

	def processDeviceSubtask(self, device):
		affectedDevices, duration = device.updateTime()

		# create follow up task in queue
		for affectedDevice in affectedDevices:
			if affectedDevice is not None:
				print("queued continue", affectedDevice)
				print(self.time + duration, CONTINUE_JOB, affectedDevice)
				self.queue.put(PrioritizedItem(self.time + duration, (CONTINUE_JOB, affectedDevice)))
			else:
				print("queuing next", device)
				self.queueNextJob(device)
		print("affected:", affectedDevices)


class QueueTask:
	def __repr__(self): return self.__name__

	__name__ = "INVALID TASK"
	def __init__(self, name):
		self.__name__ = name

NEW_JOB = QueueTask("New Job")
CONTINUE_JOB = QueueTask("Continue job")

from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
	priority: float
	item: Any=field(compare=False)