import sys
import traceback
import warnings
from queue import PriorityQueue, Empty

import numpy as np

from sim import debug
from sim.devices.components import powerPolicy
from sim.experiments.scenario import RANDOM_SCENARIO_RANDOM
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.state.extendedSystemState import extendedSystemState
from sim.simulations import constants, Simulation
from sim.simulations.Simulation import BasicSimulation
from sim.tasks.subtask import subtask


class SimpleSimulation(BasicSimulation):
	queue = None
	# autoJobs = None
	jobInterval = None
	scenario = None

	def __init__(self, numDevices=constants.NUM_DEVICES, jobInterval=constants.DEFAULT_TIME_INTERVAL, maxJobs=constants.MAX_JOBS, systemStateClass=extendedSystemState, agentClass=minimalTableAgent, allowExpansion=constants.ALLOW_EXPANSION, reconsiderBatches=False, tasks=constants.DEFAULT_TASK_GRAPH, offPolicy=constants.OFF_POLICY, scenarioTemplate=RANDOM_SCENARIO_RANDOM, centralisedLearning=constants.CENTRALISED_LEARNING):
		BasicSimulation.__init__(self, numDevices=numDevices, maxJobs=maxJobs, reconsiderBatches=reconsiderBatches, systemStateClass=systemStateClass, agentClass=agentClass, globalClock=False, allowExpansion=allowExpansion, tasks=tasks, offPolicy=offPolicy, centralisedLearning=centralisedLearning)
		# remove the taskqueues as tasks are queued in sim
		for dev in self.devices: dev.taskQueue = None

		# # overwrite device clocks so each tracks its own time (no global time)
		# for dev in self.devices:
		# 	dev.currentTime = clock(dev)
		self.time = None

		# specify subtask behaviour
		subtask.update = subtask.perform

		self.queue = PriorityQueue()
		# self.autoJobs = autoJobs
		# debug.out("job interval set to %s" self.jobInterval)
		# if self.autoJobs:
		# 	self.queueInitialJobs()

		# assert not (autoJobs and scenarioTemplate is not None)

		self.scenario = scenarioTemplate
		self.scenario.setInterval(jobInterval)
		self.queueNewJobs(self.scenario.setDevices(self.devices))

		BasicSimulation.reset(self)

	def queueInitialJobs(self):
		self.queueNewJobs(self.scenario.setDevices(self.devices))
		# need to initially check when each device's first task is
		# for dev in self.devices:
		# 	self.queueNextJob(dev)

	def reset(self):
		# remove remaining tasks from queue
		while not self.queue.empty():
			try:
				self.queue.get(False)
			except Empty:
				continue
			self.queue.task_done()
		self.scenario.reset()

		BasicSimulation.reset(self)
		self.queueInitialJobs()

	def removeDevice(self):
		BasicSimulation.removeDevice(self)

		self.scenario.setDevices(self.devices, queueInitial=False)
		# if self.autoJobs: self.queueInitialJobs()

	def performScenario(self, targetScenario):
		print("Performing scenario", targetScenario)
		for task in targetScenario.getTasks(self.devices):
			# time, taskType, device, subtask = task

			self.queueTask(*task)

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
		usages = None

		# first check if all devices are done
		if all([dev.gracefulFailure for dev in self.devices]): self.stop()
		else:
			# update offloading target for e.g. roundrobin
			if self.useSharedAgent:
				self.sharedAgent.updateOffloadingTarget()
			else:
				for dev in self.devices: dev.agent.updateOffloadingTarget()

			tasksBefore = np.array([dev.currentSubtask for dev in self.devices])

			# process new queued task here
			# newTime, arguments = self.queue.get()
			debug.out("graceful failure: %s" % [dev.gracefulFailure for dev in self.devices])
			assert self.queue.qsize() > 0

			if debug.settings.enabled:
				print("before:")
				self.printQueue()
			debug.out("states before: {0}".format([[comp.getPowerState() for comp in dev.components] for dev in self.devices]), 'y')

			assert self.queue.qsize() > 0
			nextTask = self.queue.get()
			newTime = nextTask.priority
			arguments = nextTask.item
			# print("pop", newTime, arguments)
			debug.out("new time %f %s %s" % (newTime, arguments, [dev.getNumSubtasks() for dev in self.devices]))
			debug.out("remaining tasks: %d" % self.queue.qsize(), 'dg')

			# temporarily cache tasks to print
			if debug.settings.enabled:
				self.printQueue()

			if self.stopIfEpisodeDone():
				print("EPISODE OVER")
				debug.out("EPISODE ALREADY OVER", 'r')
				return False
			# device.setTime(newTime)

			# process this queued task
			usages = self.processQueuedTask(newTime, arguments)

			# check if queues are overrun
			if self.allowExpansion:
				# check if batch is growing too big
				if np.max([dev.maxBatchLength() for dev in self.devices]) >= self.maxJobs - 1:
					if self.maxJobs - 1 < constants.ABSOLUTE_MAX_JOBS:
						# print("max jobs exceeded!")

						beforeCount = self.currentSystemState.getUniqueStates()
						# increase max jobs allowed
						self.maxJobs += 1
						for dev in self.devices: dev.maxJobs += 1
						# print("increased maxjobs", self.devices[0].maxJobs)
						field = "jobsInQueue"
						assert field in self.currentSystemState.singles
						# self.currentSystemState.expandField(field)
						if self.sharedAgent is not None:
							self.sharedAgent.expandField(field)
						else:
							for dev in self.devices: dev.agent.expandField(field)
						debug.out("expanded states %d to %d" % (beforeCount, self.currentSystemState.getUniqueStates()))

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

			self.stopIfEpisodeDone()
			# if self.systemLifetime() <= 0:
			# 	self.stop()

			# check if task queue is too long
			self.taskQueueLength = [dev.getNumSubtasks() for dev in self.devices]
			# for i in range(len(self.devices)):
			# 	if self.taskQueueLength[i] > constants.MAXIMUM_TASK_QUEUE:
			# 		# check distribution of job assignments
			# 		unique, counts = np.unique(np.array(results.chosenDestinations[:-1]), return_counts=True)
			# 		print(dict(zip(unique, counts)))

			# 		warnings.warn("TaskQueue for {} too long! {} Likelihood: {}".format(self.devices[i], len(self.devices[i].taskQueue), constants.JOB_LIKELIHOOD))

			# self.currentDelays = [dev.currentSubtask.delay if dev.currentSubtask is not None else 0 for dev in self.devices]
			# self.delays.append(self.currentDelays)

			# print all results if interesting
			tasksAfter = np.array([dev.currentSubtask for dev in self.devices])
			if debug.settings.enabled:
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
				debug.out("states after: {0}".format([[comp.getPowerState() for comp in dev.components] for dev in self.devices]), 'y')
				debug.out("tasks after {0}".format(tasksAfter), 'r')

				# if np.sum(self.currentDelays) > 0:
				# 	debug.out("delays {}".format(self.currentDelays))
		return usages
	# # if constants.DRAW_DEVICES:
	# if self.frames % self.plotFrames == 0:
	# 	self.visualiser.update()

	# progress += constants.TD

	# add next job to be created for this device to backlog
	def queueNextJob(self, device, currentJobTime):
		# print("queue next job", currentJobTime)
		nextTime, nextDevice = self.scenario.nextJob(device, currentJobTime)
		# print("queue", nextTime, nextDevice)
		# print("current:", currentJobTime, "nextTime:", nextTime)
		self.queueTask(nextTime, NEW_JOB, nextDevice)
	# def queueNextJob(self, device, currentTime=None):
	# 	assert device is not None
	#
	# 	if currentTime is None:
	# 		currentTime = device.currentTime.current
	#
	# 	# next job in:
	# 	nextInterval = self.jobInterval.gen()
	# 	nextJob = currentTime + nextInterval
	#
	# 	# print("next job is at", nextJob, device)
	# 	# add task to queue
	# 	self.queueTask(nextJob, NEW_JOB, device)

	# def continueScenario(self):
	# 	self.queueTask(self.scenario.nextJob())

	# print("new", self.time, nextJob)

	previous = None
	latestDevice = None

	# do next queued task
	def processQueuedTask(self, scheduledTime, args):
		task = args[0]
		device = args[1]
		# print("simple:", task, device, scheduledTime)
		debug.out("%f: task is %s %s" % (scheduledTime, task, device), 'g')
		device.queuedTask = None
		self.latestDevice = device
		usages = []

		# perform queued task
		if task == NEW_JOB:
			debug.out("creating new job", 'b')
			device = args[1]
			# check job needs to be reassigned
			if device.gracefulFailure:
				olddevice = device
				device = self.scenario.reassignJob(device)
				debug.out("reassigned job from %s to %s" % (olddevice, device))

			if not device.gracefulFailure:
				self.createNewJob(device)
				self.queueNextJob(device, scheduledTime)

				# immediately start created job if not busy
				affectedDevice = device.nextJob()
				# print("affecteddevice", affectedDevice)
				# no devices affected if already has job
				if affectedDevice is not None:
					# start created subtask
					nextdevice, nextsubtask = affectedDevice
					debug.out("new job affected: %s %s" % (nextdevice, nextsubtask), 'b')
					self.queueTask(scheduledTime, PROCESS_SUBTASK, nextdevice, nextsubtask)
					print("queueing initial subtask", scheduledTime, nextdevice, nextsubtask)
					# self.processAffectedDevice(affectedDevice)

			else:
				debug.out("not creating new job because %s in graceful failure" % args[1])
		#
		# device.updatePreviousTimestamp(self.time.current)
		# debug.out("")
		elif task == PROCESS_SUBTASK:
			# energy from idle period
			# TODO: check that this idle period is correct
			# TODO: if schedule is missed, adjust scheduled time
			debug.out("idle %s: %s %.6f (%.6f)" % (device, scheduledTime, device.currentTime.current, scheduledTime - device.currentTime.current), 'b')
			# idlePeriod = device.currentTime.current - device.previousTimestamp
			idlePeriod = scheduledTime - device.currentTime.current


			# scheduled time wasn't available
			if idlePeriod < 0:
				debug.out("scheduled time wasn't available: %f (%f)" % (scheduledTime, idlePeriod), 'r')

				scheduledTime = device.currentTime.current
				idlePeriod = 0

			# if idlePeriod >= 0:
			# idlePower = device.getTotalPower()

			if device.asleep():
				device.incremementTotalSleepTime(idlePeriod)

			# idle power
			debug.out("%s idle %f" % (device, idlePeriod), 'r')
			device.currentTd = idlePeriod
			devicePower = device.getTotalPower()
			device.updateDeviceEnergy(devicePower)
			usages.append([idlePeriod, devicePower])
			debug.out("idle %s time handled to %f (%f)" % (device, device.currentTime.current, device.previousTimestamp), 'p')
			if idlePeriod > 0:
				debug.infoOut('idle energy %.2f %.2f %.2f%% %s' % (idlePeriod, devicePower, idlePeriod * devicePower / device.maxEnergyLevel * 100., device.getComponentStates()))

			# check if idle killed device
			if device.energyLevel < 0:
				debug.out("DEVICE DEAD", 'r')
				return

			debug.out("continue existing job", 'b')
			subtask = args[2]  # none for new_job
			self.processDeviceSubtask(device, subtask)
			usages.append((subtask.duration, device.latestPower))

		elif task == SLEEP_COMPONENT:
			# check if device should be sleeping
			debug.out("CHECKING DEVICE SLEEP")
			# self.timeOutSleep(device)
			device.timeOutSleepFpga()

		self.previous = (device.currentTime.current, args, self.queue.qsize())
		return usages
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

	def queueNewJobs(self, jobs):
		for time, device in jobs:
			self.queueTask(time, NEW_JOB, device)


	def queueTask(self, time, taskType, device, subtask=None):
		# check if this device has a task lined up already:
		# if device.queuedTask is None:
		assert device is not None
		debug.out("queueing task %f %s %s %s" % (time, taskType, device, subtask), 'r')
		newTask = PrioritizedItem(time, (taskType, device, subtask))
		self.queue.put(newTask)
		# print("queue:")
		# self.printQueue()
		device.queuedTask = newTask

	# eoh m# 	print("device", device, "already has queued item!", self.queue)

	def processAffectedDevice(self, affectedDevice):
		device, subtask = affectedDevice

	# 	# if device already has assigned subtask and this is just to create a new task, reschedule
	# 	if device.currentSubtask is not None and device.currentSubtask != subtask:
	# 		debug.out("Rescheduling %s because %s is already doing %s" % (subtask, device, device.currentSubtask), 'r')
	# 		self.queueTask(device.currentTime + device.currentSubtask.duration, PROCESS_SUBTASK, device, subtask)
	# 	else:
		self.processDeviceSubtask(device, subtask)

	def processDeviceSubtask(self, device, subtask):
		# assert affected is not None

		# device, subtask = affected
		print("sim:", device, subtask)
		hasOffspring = False
		visualiser = None
		# decide whether to pass in visualiser or not
		self.frames += 1
		if self.frames % self.plotFrames == 0:
			visualiser = self.visualiser  # this will trigger an update

		# perform subtask here
		debug.out("processing device subtask: %s %s" % (device, subtask))
		affectedDevices, duration, devicePower = device.updateDevice(subtask, visualiser=visualiser)
		# do not assign new jobs to this device
		if device.gracefulFailure:
			self.scenario.removeDevice(device)
		timeBefore = device.currentTime.current
		timeAfter = timeBefore + subtask.duration

		# error in simulation (likely end state)
		if affectedDevices is None:
			return False
		# assert affectedDevices is not None

		# update device energy
		assert duration != constants.TD
		device.currentTd = duration
		incrementalEnergy = device.updateDeviceEnergy(devicePower)
		currentJob = device.currentJob

		# if not associated with job, nothing to increment energy cost of
		if currentJob is not None:
			currentJob.addEnergyCost(incrementalEnergy, device)

		try:
			# create follow up task in queue
			for affectedDevice in affectedDevices:
				if affectedDevice is not None:
					nextDevice, nextSubtask = affectedDevice
					# next task begins at

					# queue based on when next task is finished
					# nextTaskFinished = nextTask + subtask.duration
					# print("continue", subtask, self.time, duration, nextTask, nextTaskFinished)
					self.queueTask(timeAfter, PROCESS_SUBTASK, nextDevice, nextSubtask)
					hasOffspring = True

		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_stack()
			traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
			sys.exit(0)

		# queue task to check if device should sleep
		# print(constants.FPGA_POWER_PLAN, device.fpga.getPowerState())
		if constants.FPGA_POWER_PLAN == powerPolicy.IDLE_TIMEOUT:
			if device.fpga.isIdle() and device.fpga.latestActive is not None:
				self.queueTask(timeBefore + constants.FPGA_IDLE_SLEEP, SLEEP_COMPONENT, device)
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

	# def timeOutSleep(self, target):
	# 	# call on any contained FPGAs
	# 	if isinstance(target, node):
	# 		for targetProcessor in target.processors:
	# 			# mcu sleeping is managed in subtask finish
	# 			if isinstance(targetProcessor, fpga):
	# 				self.timeOutSleep(targetProcessor)
	#
	# 	else:
	# 		assert isinstance(target, processor)
	# 		if target.isIdle():
	# 			idleTime = target.owner.currentTime - target.latestActive
	# 			# debug.out("sleep check: %s %s %f %f %s" % (target, target.isIdle(), idleTime, target.idleTimeout, target.owner.currentTd))
	# 			# print("sleep check: %s %s %f %f %s" % (target, target.isIdle(), idleTime, target.idleTimeout, target.owner.currentTd))
	#
	# 			# target.idleTime += target.owner.currentTd
	# 			if idleTime >= target.idleTimeout:
	# 				target.sleep()
	# 				debug.out("target SLEEP")
	# 		# else:
	# 		else:
	# 			target.idleTime = 0


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


