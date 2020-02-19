import sys
import traceback
import warnings
from queue import PriorityQueue, Empty

import numpy as np

from sim import debug
from sim.clock import clock
from sim.devices.components import powerPolicy
from sim.devices.components.processor import processor
from sim.devices.components.fpga import fpga
from sim.devices.node import node
from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.offloading import offloadingPolicy, offloadingDecision
from sim.simulations import constants
from sim.simulations.Simulation import BasicSimulation
from sim.tasks.subtask import subtask


class SimpleSimulation(BasicSimulation):
	queue = None
	autoJobs = None

	def __init__(self, systemStateClass=minimalSystemState,
				 offloadingDecisionClass=offloadingDecision.offloadingDecision, agentClass=minimalAgent, autoJobs=True):
		BasicSimulation.__init__(self, systemStateClass=systemStateClass,
								 offloadingDecisionClass=offloadingDecisionClass, agentClass=agentClass, globalClock=False)

		# # overwrite device clocks so each tracks its own time (no global time)
		# for dev in self.devices:
		# 	dev.currentTime = clock(dev)
		self.time = None

		# specify subtask behaviour
		subtask.update = subtask.perform

		self.queue = PriorityQueue()
		self.autoJobs = autoJobs
		if self.autoJobs:
			self.queueInitialJobs()

	def queueInitialJobs(self):
		# need to initially check when each device's first task is
		for dev in self.devices:
			self.queueNextJob(dev)

	def reset(self):
		# remove remaining tasks from queue
		while not self.queue.empty():
			try:
				self.queue.get(False)
			except Empty:
				continue
			self.queue.task_done()

		BasicSimulation.reset(self)
		if self.autoJobs: self.queueInitialJobs()

	# reset energy levels of all devices and run entire simulation
	def simulateQueuedTasks(self, reset=True):
		if reset: self.reset()
		i = 0
		while not self.finished and not self.queue.empty():
			# print("tick", i)
			i += 1
			self.simulateTick()
		self.episodeNumber += 1

	def simulateTick(self):
		debug.out("\n" + "*" * 50 + "\ntick\n" + "*" * 50)

		# update state if required
		# if constants.OFFLOADING_POLICY == offloadingPolicy.REINFORCEMENT_LEARNING:
		# 	self.currentSystemState.updateSystem()

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
		assert self.queue.qsize() > 0

		print("before:")
		self.printQueue()
		debug.out("states: {0}".format([[comp.getPowerState() for comp in dev.components] for dev in self.devices]), 'y')

		nextTask = self.queue.get()
		newTime = nextTask.priority
		arguments = nextTask.item
		debug.out("new time %f %s %s" % (newTime, arguments, [dev.getNumSubtasks() for dev in self.devices]))
		debug.out("remaining tasks: %d" % self.queue.qsize(), 'dg')

		# temporarily cache tasks to print
		if debug.enabled:
			self.printQueue()

		# device.setTime(newTime)
		self.processQueuedTask(newTime, arguments)
		# print("popped time", newTime, arguments)

		# # should always have task lined up for each device
		# assert self.queue.qsize() == len(self.devices)

		# # update all the devices
		# for dev in self.devices:
		# 	if not (dev.currentJob is None and dev.currentSubtask is None):
		# 		debug.out('\ntick device [{}] [{}] [{}]'.format(dev, dev.currentJob, dev.currentSubtask))
		# 	dev.updateTime(self.time)
		# 	queueLengths.append(len(dev.jobQueue))

		if constants.DRAW_GRAPH_EXPECTED_LIFETIME:
			# note energy levels for plotting
			self.timestamps.append(self.time)
			self.lifetimes.append(self.devicesLifetimes())
			self.energylevels.append(self.devicesEnergyLevels())

		if self.systemLifetime() <= 0:
			self.stop()

		# check if task queue is too long
		self.taskQueueLength = [dev.getNumSubtasks() for dev in self.devices]
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
		if debug.enabled:
			# if not (np.all(tasksAfter == None) and np.all(tasksBefore == None)):
			debug.out('tick {}'.format(self.time), 'b')
			# 	debug.out("nothing...")
			# else:
			debug.out("tasks before {0}".format(tasksBefore), 'r')
			debug.out("have jobs:\t{0}".format([dev.hasJob() for dev in self.devices]), 'b')
			debug.out("jobQueues:\t{0}".format([dev.getNumJobs() for dev in self.devices]), 'g')
			debug.out("batchLengths:\t{0}".format(self.batchLengths()), 'c')
			debug.out("currentBatch:\t{0}".format([dev.currentBatch for dev in self.devices]))
			debug.out("currentConfig:\t{0}".format([dev.getFpgaConfiguration() for dev in self.devices]))
			debug.out("taskQueues:\t{0}".format([dev.getNumSubtasks() for dev in self.devices]), 'dg')
			# debug.out("taskQueues:\t{0}".format([[task for task in dev.taskQueue] for dev in self.devices]), 'dg')
			debug.out("states: {0}".format([[comp.getPowerState() for comp in dev.components] for dev in self.devices]), 'y')
			debug.out("tasks after {0}".format(tasksAfter), 'r')

			if np.sum(self.currentDelays) > 0:
				debug.out("delays {}".format(self.currentDelays))

	# # if constants.DRAW_DEVICES:
	# if self.frames % self.plotFrames == 0:
	# 	self.visualiser.update()

	# progress += constants.TD

	# add next job to be created for this device to backlog
	def queueNextJob(self, device, currentTime=None):
		assert device is not None

		if currentTime is None:
			currentTime = device.currentTime.current

		# next job in:
		nextInterval = constants.JOB_INTERVAL.gen()
		nextJob = currentTime + nextInterval

		# print("next job is at", nextJob, device)
		# add task to queue
		self.queueTask(nextJob, NEW_JOB, device)

	# print("new", self.time, nextJob)

	previous = None

	# do next queued task
	def processQueuedTask(self, scheduledTime, args):
		task = args[0]
		device = args[1]
		debug.out("task is %s %s" % (task, device))
		device.queuedTask = None

		# perform queued task
		if task == NEW_JOB:
			debug.out("creating new job", 'b')
			device = args[1]
			self.createNewJob(device)

			# immediately start created job if not busy
			affectedDevice = device.nextJob()
			# no devices affected if already has job
			if affectedDevice is not None:
				# start created subtask
				debug.out("new job affected: %s %s" % (affectedDevice), 'b')
				self.processAffectedDevice(affectedDevice)

			if self.autoJobs:
				self.queueNextJob(device, scheduledTime)
		#
		# device.updatePreviousTimestamp(self.time.current)
		# debug.out("")
		elif task == PROCESS_SUBTASK:
			# energy from idle period
			# TODO: check that this idle period is correct
			# TODO: if schedule is missed, adjust scheduled time
			debug.out("idle %s: %s %.6f (%.6f)" % (device, scheduledTime, device.currentTime.current, scheduledTime - device.currentTime.current), 'r')
			# idlePeriod = device.currentTime.current - device.previousTimestamp
			idlePeriod = scheduledTime - device.currentTime.current
			print(device.currentTime.owner)
			if idlePeriod >= 0:
				# idlePower = device.getTotalPower()
				debug.out("%s idle %f" % (device, idlePeriod), 'r')
				device.currentTd = idlePeriod
				device.updateDeviceEnergy(device.getTotalPower())
				device.updatePreviousTimestamp(device.currentTime.current)
				debug.out("idle %s time handled to %f (%f)" % (device, device.currentTime.current, device.previousTimestamp), 'p')
			else:
				warnings.warn("going back in time!")
				print()
				print()
				print(device.currentTime.current, device.previousTimestamp, device.currentTime - device.previousTimestamp, device)
				print("args", args, self.queue.qsize())
				print("previous", self.previous)
				print(device.__dict__)
				print()
				print()
				# traceback.print_stack()
				raise Exception("This doesn't make sense")

			debug.out("continue existing job", 'b')
			subtask = args[2]  # none for new_job
			self.processDeviceSubtask(device, subtask)

		elif task == SLEEP_COMPONENT:
			# check if device should be sleeping
			print("CHECKING DEVICE SLEEP")
			print([com.isSleeping() for com in device.components])
			self.timeOutSleep(device)
			print([com.isSleeping() for com in device.components])

		self.previous = (device.currentTime.current, args, self.queue.qsize())

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

	# # only allow one queued task per device
	# assert self.queue.qsize() <= len(self.devices)

	def queueTask(self, time, taskType, device, subtask=None):
		# check if this device has a task lined up already:
		# if device.queuedTask is None:
		assert device is not None
		debug.out("queueing task %f %s %s %s" % (time, taskType, device, subtask), 'r')
		newTask = PrioritizedItem(time, (taskType, device, subtask))
		self.queue.put(newTask)
		device.queuedTask = newTask

	# eoh m# 	print("device", device, "already has queued item!", self.queue)

	def processAffectedDevice(self, affectedDevice):
		device, subtask = affectedDevice

		# if device already has assigned subtask and this is just to create a new task, reschedule
		if device.currentSubtask is not None:
			debug.out("Rescheduling %s because %s is already doing %s" % (subtask, device, device.currentSubtask), 'r')
			self.queueTask(device.currentTime + device.currentSubtask.duration, PROCESS_SUBTASK, device, subtask)
		else:
			self.processDeviceSubtask(device, subtask)

	def processDeviceSubtask(self, device, subtask):
		# assert affected is not None

		# device, subtask = affected

		hasOffspring = False
		visualiser = None
		# decide whether to pass in visualiser or not
		self.frames += 1
		if self.frames % self.plotFrames == 0:
			visualiser = self.visualiser  # this will trigger an update

		# perform subtask here
		debug.out("processing device subtask: %s %s" % (device, subtask))
		affectedDevices, duration, devicePower = device.updateDevice(subtask, visualiser=visualiser)
		taskEnding = device.currentTime.current

		assert affectedDevices is not None

		# update device energy
		assert duration != constants.TD
		device.currentTd = duration
		incrementalEnergy = device.updateDeviceEnergy(devicePower)
		currentJob = device.currentJob

		# if not associated with job, nothing to increment energy cost of
		if currentJob is not None:
			currentJob.addEnergyCost(incrementalEnergy)

		try:
			# create follow up task in queue
			for affectedDevice in affectedDevices:
				if affectedDevice is not None:
					nextDevice, nextSubtask = affectedDevice
					# next task begins at


					# queue based on when next task is finished
					# nextTaskFinished = nextTask + subtask.duration
					# print("continue", subtask, self.time, duration, nextTask, nextTaskFinished)
					self.queueTask(taskEnding, PROCESS_SUBTASK, nextDevice, nextSubtask)
					hasOffspring = True

		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_stack()
			traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
			sys.exit(0)

		# queue task to check if device should sleep
		print(constants.FPGA_POWER_PLAN, device.fpga.getPowerState())
		if constants.FPGA_POWER_PLAN == powerPolicy.IDLE_TIMEOUT:
			if device.fpga.isIdle():
				self.queueTask(taskEnding + constants.FPGA_IDLE_SLEEP, SLEEP_COMPONENT, device)
		# if constants.MCU_POWER_PLAN == powerPolicy.IDLE_TIMEOUT:
		# 	if not device.mcu.isSleeping():
		# 		self.queueTask(nextTask + constants.MCU_IDLE_SLEEP, SLEEP_COMPONENT, device)

		# update device time
		# device.currentTime.set(taskEnding)

		return hasOffspring
		# return duration

	def printQueue(self):
		temp = []
		beforeTasks = self.queue.qsize()
		while not self.queue.empty():
			temp.append(self.queue.get())
		for t in temp: self.queue.put(t)
		print(temp)

		assert self.queue.qsize() == beforeTasks

	def timeOutSleep(self, target):
		# call on any contained FPGAs
		if isinstance(target, node):
			for targetProcessor in target.processors:
				# mcu sleeping is managed in subtask finish
				if isinstance(targetProcessor, fpga):
					self.timeOutSleep(targetProcessor)

		else:
			assert isinstance(target, processor)
			if target.isIdle():
				idleTime = target.owner.currentTime - target.latestActive
				print(target, target.isIdle(), idleTime, target.idleTimeout, target.owner.currentTd)

				# target.idleTime += target.owner.currentTd
				if idleTime >= target.idleTimeout:
					target.sleep()
					debug.out("target SLEEP")
			# else:
			else:
				target.idleTime = 0


class QueueTask:
	def __repr__(self): return self.__name__

	__name__ = "INVALID TASK"

	def __init__(self, name):
		self.__name__ = name


NEW_JOB = QueueTask("New Job")
PROCESS_SUBTASK = QueueTask("Process Subtask")
SLEEP_COMPONENT = QueueTask("Sleep Component")

from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PrioritizedItem:
	priority: float
	item: Any = field(compare=False)

	def __repr__(self): return "(%.6f - %s)" % (self.priority, self.item)


