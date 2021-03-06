import sys
import time
import warnings
from queue import PriorityQueue
from sys import stdout

import numpy as np

import sim.debug
import sim.devices.components.processor
import sim.simulations.constants
import sim.tasks.job
import sim.tasks.subtask
from sim import debug
from sim.clock import clock
from sim.devices.components.fpga import fpga
from sim.learning.action import BATCH, LOCAL
from sim.simulations import constants


class node:
	# message = None
	# decision = None
	jobQueue = None
	taskQueue = None
	currentJob = None
	# queuedTask = None # used in simple simulation
	hasJobScheduled = None # used in simple simulation
	previousTimestamp = None
	numJobs = None
	numJobsDone = None
	numTasksDone = None
	currentSubtask = None
	index = None

	energyLevel = None
	maxEnergyLevel = None
	totalEnergyCost = None
	averagePower = None
	powerCount = None
	latestPower = None
	totalSleepTime = None
	drawLocation = None
	gracefulFailure = False
	gracefulFailureLevel = None
	offloadingOptions = None
	defaultOffloadingOptions = []

	platform = None
	components = None
	processors = None
	jobActive = None
	alwaysHardwareAccelerate = None

	batch = None
	currentBatch = None
	batchFull = None
	# reconsiderBatches = None
	maxJobs = None

	currentTime = None
	currentTd = None # amount of current TD that this node is busy

	# drawing
	rectangle = None
	location = None
	# episodeFinished = None

	def __init__(self, inputClock, platform, index, components, reconsiderBatches, maxJobs, currentSystemState=None, agent=None, alwaysHardwareAccelerate=None, offPolicy=constants.OFF_POLICY, trainClassification=True):
		self.platform = platform

		# self.decision = offloadingDecisionClass(self, currentSystemState, agentClass)

		# if agentClass is a class, create private
		if type(agent) is type(__class__):
			# print("agent class", agent)
			self.agent = agent(systemState=currentSystemState, owner=self, offPolicy=offPolicy,reconsiderBatches=reconsiderBatches, trainClassification=trainClassification)
		else:
			self.agent = agent

		if inputClock is None:
			self.currentTime = clock(self)
		else:
			self.currentTime = inputClock

		# self.resultsQueue = queue
		self.index = index
		# print("created index", index)
		self.maxJobs = maxJobs
		# self.nodeType = nodeType
		# self.reconsiderBatches = reconsiderBatches

		self.setMaxEnergyLevel()
		self.gracefulFailureLevel = currentSystemState.getGracefulFailureLevel()
		# print('graceful death level set to', self.gracefulFailureLevel)
		# sys.exit(0)

		self.drawLocation = (0,0)

		self.setComponents(components)
		self.reset(0)
		# self.episodeFinished = episodeFinished
		self.alwaysHardwareAccelerate = alwaysHardwareAccelerate

	def setMaxEnergyLevel(self, batterySize=constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE):
		self.maxEnergyLevel = node.convertEnergy(batterySize, self.platform.BATTERY_VOLTAGE)
		self.resetEnergyLevel()

	def setTime(self, newTime):
		self.currentTime.set(newTime)

	def reset(self, episodeNumber):
		self.previousTimestamp = 0
		self.jobQueue = PriorityQueue()
		self.currentJob = None
		self.currentSubtask = None
		self.currentBatch = None
		if self.taskQueue is not None:
			self.taskQueue = PriorityQueue()
		sim.debug.out("jobqueue" + str(self.jobQueue))
		self.hasJobScheduled = False
		
		self.resetEnergyLevel()
		self.averagePower = 0.05
		self.latestPower = 0
		self.powerCount = 0
		self.totalEnergyCost = 0
		self.totalSleepTime = 0
		self.jobActive = False
		self.numJobs = 0
		self.numJobsDone = 0
		self.numTasksDone = dict()
		self.batch = dict()
		self.currentTime.reset()

		# first run the components can be None
		if self.components is not None:
			for com in self.components:
				com.reset()

		self.agent.reset(episodeNumber)
		self.offloadingOptions = list(self.defaultOffloadingOptions)

	def resetEnergyLevel(self):
		self.energyLevel = self.maxEnergyLevel
		self.gracefulFailure = False

	# get node battery level, limited to different discrete bins if required
	def getEnergyLevel(self):
		return self.energyLevel

	# get node battery level, limited to different discrete bins if required
	def getEnergyLevelPercentage(self):
		return self.energyLevel / self.maxEnergyLevel


	def setComponents(self, components):
		if components is None:
			return
		self.components = components
		self.processors = [component for component in self.components if isinstance(component, sim.devices.components.processor.processor)]
		# for processor in self.processors:
		# 	processor.timeOutSleep()


	@staticmethod
	# convert mAh to Joule
	def convertEnergy(mah, voltage):
		return mah * voltage * 3.6

	def __repr__(self):
		return "<" + str(type(self)) + " " + str(self.index) + ">"

	def setOffloadingOptions(self, allDevices):
		self.offloadingOptions = []
		for device in self.agent.getOffloadingTargets(allDevices):
			if device is not self:
				self.offloadingOptions.append(device)
		self.defaultOffloadingOptions = list(self.offloadingOptions)
		debug.out("set offloading options for %s to %s" % (self, self.offloadingOptions))

	def removeOffloadingOption(self, device):
		if device in self.offloadingOptions:
			self.offloadingOptions.remove(device)
			debug.learnOut("removed offloading option %s %s" % (device, self.offloadingOptions))

	def removeDefaultOffloadingOption(self, device):
		if device in self.defaultOffloadingOptions:
			self.defaultOffloadingOptions.remove(device)

	# def setOptions(self, options):
		# self.setOffloadingDecisions(options)

	# def setOffloadingDecisions(self, devices):
	# 	self.agent.setOptions(devices)

	def getCurrentConfiguration(self):
		# default behaviour is to not have a configuration
		return 0

	def getNumTasksDone(self, taskname):
		if taskname not in self.numTasksDone:
			return 0
		else:
			return self.numTasksDone[taskname]

	def incrementTaskDone(self, taskname):
		if taskname not in self.numTasksDone:
			self.numTasksDone[taskname] = 1
		else:
			self.numTasksDone[taskname] += 1

	def hasFpga(self):
		return np.any([isinstance(component, fpga) for component in self.processors])

	def hasJob(self):
		# busy if any are busy
		return self.currentJob is not None

		# return self.jobActive # or self.waitingForResult or np.any([device.busy for device in self.components])
		# return len(self.jobQueue) > 0
	# def prependTask(self, subtask):
	# 	self.jobQueue = [subtask] + self.jobQueue



	# set active batch and activate this job
	def setActiveJob(self, job):
		# grab first task
		sim.debug.out("activating job")
		self.currentJob = job
		self.setCurrentBatch(job)

		# start first job in queue
		# print("newjob in setactivejob")
		return sim.tasks.subtask.newJob(job)

	# appends one job to the end of the task queue (used for queueing future tasks)
	def addSubtask(self, task):
		task.owner = self
		sim.debug.out("adding subtask %s %s" % (str(task), str(self)), 'b')

		# prioritised tasks without jobs (batchContinue mostly)
		taskPriority = task.job\
			if task.job is not None else 0
		# some simulations remove task queues (because they are queued elsewhere)
		if self.taskQueue is not None:
			self.taskQueue.put(PrioritizedItem(taskPriority, task))

			# # if added by another device (e.g. rxmessage), do not activate yet
			# if device is None or device == self:
			# if nothing else happening, start task
			self.nextTask()

	# used in deadlock resolving
	# def removeTask(self, task):
	# 	sim.debug.out("REMOVE TASK {0}".format(task))
	# 	self.taskQueue.remove(task)
	# 	sim.debug.out("{} {}".format(self.currentSubtask, task))
	# 	if self.currentSubtask is task:
	# 		self.currentSubtask = None
	# 		sim.debug.out ("next task...")
	# 		self.nextTask()

	def nextTask(self):
		# only change task if not performing one at the moment
		if self.currentSubtask is None:
			# check if there is another task is available
			if self.hasSubtask():
				nextSubTask = self.taskQueue.get()
				self.currentSubtask = nextSubTask.item
				sim.debug.out("next subtask %s from %s" % (nextSubTask, nextSubTask.priority))
				# # do receive tasks first, because other device is waiting
				# for task in self.taskQueue:
				# 	if isinstance(task, sim.subtask.rxMessage):
				# 		self.currentSubtask = task
				# 		self.taskQueue.remove(task)
				# 		break
				# # if still nothing, do a normal task
				# if self.currentSubtask is None:
				# 	# if any of the tasks have been started continue that
				# 	for task in self.taskQueue:
				# 		if task.started:
				# 			self.currentSubtask = task
				# 			self.taskQueue.remove(task)
				# 			break
				#
				# 	# lastly, see if tx messages are available
				# 	if self.currentSubtask is None:
				# 		# do receive tasks first, because other device is waiting
				# 		for task in self.taskQueue:
				# 			if isinstance(task, sim.subtask.txMessage):
				# 				self.currentSubtask = task
				# 				self.taskQueue.remove(task)
				# 				break
				#
				# 		# if nothing else to do, just do the oldest task that isn't a new job
				# 		if self.currentSubtask is None:
				# 			self.currentSubtask = self.taskQueue.popleft()

				# if len(self.taskQueue) > 1:
				if self.getNumSubtasks() > 1:
					sim.debug.out("")
					sim.debug.out("nextTask: {} {}".format(self.currentSubtask, self.taskQueue))
					sim.debug.out("")
					
				# self.currentTask = self.taskQueue[0]
				# remove from queue because being processed now
				# self.taskQueue.remove(self.currentTask)

				self.currentSubtask.owner = self
				sim.debug.out(str(self) + " NEXT TASK " + str(self.currentSubtask))

			else:
				# sim.debug.out("no next task")
				self.currentSubtask = None

	def getNumJobs(self):
		return self.jobQueue.qsize()

	def getNumSubtasks(self):
		if self.taskQueue is None:
			return None
		else:
			return self.taskQueue.qsize()

	# check if this node has a subtask lined up
	def hasSubtask(self):
		# return len(self.taskQueue) > 0
		return self.getNumSubtasks() > 0


	# try another task if this one is stuck
	def swapTask(self):
		sim.debug.out(self, "SWAPPING TASK\n\n\n\n")
		if sim.debug.enabled: 
			time.sleep(.1)
		# move current task to queue to be done later
		self.addSubtask(self.currentSubtask) # current task not None so nextTask won't start this task again
		self.currentSubtask = None
		self.nextTask()

	def asleep(self):
		for component in self.components:
			# if anything awake, device not sleeping
			if not component.isSleeping():
				return False
		# if it gets here, nothing is awake
		return True

	# reconsider each job in batch, maybe start it. return which device (if any) is affected
	def reconsiderBatch(self):
		sim.debug.learnOut("deciding whether to continue batch ({}) or not".format(self.batchLengths()), 'b')
		# sim.debug.out("Batch before: {0}/{1}".format(self.batchLength(self.currentJob.currentTask), sim.constants.MINIMUM_BATCH), 'c')
		sim.debug.out("Batch lengths before reconsider: {}".format(self.batchLengths()), 'c')
		for batchName in self.batch:
			currentBatch = self.batch[batchName]
			for job in currentBatch:
				sim.debug.out("considering job from batch {}".format(job))
				newChoice = self.agent.redecideDestination(job.currentTask, job, self)
				sim.debug.out("new decision: %s" % newChoice)
				# print("updated", newChoice)
				# check if just batching
				if newChoice == BATCH or newChoice.offloadingToTarget(self.index):  # (isinstance(newChoice, sim.offloadingDecision.offloading) and newChoice.targetDeviceIndex == self.owner.index):
					sim.debug.learnOut("just batching again: {}".format(newChoice), 'p')
				else:
					# update destination
					sim.debug.learnOut("changing decision to {}".format(newChoice), 'p')
					job.setDecisionTarget(newChoice)

					# remove it from the batch
					self.removeJobFromBatch(job)
					self.currentJob = job
					return job.activate()

		sim.debug.out("Batch lengths after reconsider: {}".format(self.batchLengths()), 'c')
		return None
		# sim.debug.out("Batch after: {0}/{1}".format(self.currentJob.processingNode.batchLength(self.job.currentTask), sim.constants.MINIMUM_BATCH), 'c')

	def continueBatch(self, previousJob):
		# assert task in self.batch
		assert self.currentBatch is not None

		if self.batchLength(self.currentBatch) == 0:
			debug.learnOut("no more in batch %s for %s" % (self.currentBatch, self))
			# print("batch done", self.currentBatch)
			self.currentJob = None
			return None
		debug.learnOut("continue batch for %s (%d)" % (self.currentBatch, self.batchLength(self.currentBatch)))
		# for name in self.batch:
		# 	print("name", name)
		# 	for j in self.batch[name]:
		# 		print(j,)
		# assert task == self.currentBatch

		# decide whether to continue with batch or not
		possibleNextJob = self.batch[self.currentBatch][0]
		if self.agent.reconsiderBatches:
			newChoice = self.agent.redecideDestination(possibleNextJob.currentTask, possibleNextJob, self)
			debug.learnOut("decided to continue batch at %s?: %s" % (possibleNextJob, newChoice))

			proceed = newChoice != BATCH

		else:
			# always continue batch
			newChoice = self.agent.getAction(LOCAL)
			# possibleNextJob.latestAction = self.agent.getActionIndex(newChoice)
			debug.learnOut("default to continue batch: %s" % newChoice)
			proceed = True

		if proceed:
			possibleNextJob.setDecisionTarget(newChoice)

		# if decided to continue with this batch
		if proceed:
			if self.batchLength(self.currentBatch) > 0:
				self.currentJob = self.batch[self.currentBatch][0]
				# previousJob is destroyed if offloaded due to graceful failure
				if not self.gracefulFailure:
					self.currentJob.combineJobs(previousJob)
				self.removeJobFromBatch(self.currentJob)

				return self.currentJob.activate()

			else:
				raise Exception("wanted to continue with batch but nothing available")
		else:
			self.currentJob = None

		return None

	# calculate the energy at the current activity of all the components
	def energy(self): # , duration=sim.constants.TD):
		assert self.currentTd is not None
		# totalPower = 0
		# for component in self.components:
			# totalPower += component.power()
		
		totalPower = self.getTotalPower()

		if totalPower >= 1:
			sim.debug.out("massive power usage!")
			# sim.debug.enabled = True

		return self.updateDeviceEnergy(totalPower)

	def updateDeviceEnergy(self, totalPower):
		self.updateAveragePower(totalPower)
		assert self.currentTd is not None
		incrementalEnergy = totalPower * self.currentTd
		# ensure only using each time diff once
		self.totalEnergyCost += incrementalEnergy
		# TODO: assuming battery powered
		# print (incrementalEnergy)
		self.energyLevel -= incrementalEnergy
		self.latestPower = totalPower
		# print(self.currentTd, "@", totalPower)
		debug.out("updating device energy %f %f %f %f" % (self.currentTd, incrementalEnergy, self.totalEnergyCost, self.energyLevel))

		# update device time if local time used
		if self.currentTime is not None:
			self.previousTimestamp = self.currentTime.current
			self.currentTime.increment(self.currentTd)

		self.currentTd = None

		return incrementalEnergy

	def getComponentStates(self):
		return [component.getPowerState() for component in self.components]

	def getTotalPower(self):
		# calculate total power for all components
		totalPower = 0
		for component in self.components:
			# print("component", component, component.getPowerState())
			totalPower += component.power()
		# 	stdout.write("%f " % component.power())
		# stdout.write("\n")
		# stdout.flush()


		return totalPower

	def updateAveragePower(self, power):
		self.powerCount += 1
		# 1/n
		# self.averagePower += 1.0 / self.powerCount * (power - self.averagePower) 
		# alpha
		self.averagePower += sim.simulations.constants.EXPECTED_LIFETIME_ALPHA * (power - self.averagePower)
		# sim.debug.out("average power: {}, {}".format(power, self.averagePower))

	def getAveragePower(self):
		return (self.maxEnergyLevel - self.energyLevel) / self.currentTime.current

	def updateDevice(self, subtask=None, visualiser=None):
		affectedDevices = None
		affectedDevice = None
		devicePower = 0
		# if no jobs available, perhaps generate one

		debug.out("update device %s: %s (%s) [%s]" % (self, self.currentSubtask, self.currentJob, subtask), 'g')
		if subtask is None:
			# see if there's a job available
			if self.currentJob is None:
				# print(self, "next job")
				self.nextJob()
				debug.out("next job: %s" % self.currentJob)
			# restarting existing job
			elif self.currentJob.started and not self.currentJob.active:
				sim.debug.out("restarting existing job", 'r')
				affectedDevice = self.currentJob.activate()

			# check if there's something to be done now
			if self.currentSubtask is None:
				self.nextTask()
				debug.out("next subtask: %s" % self.currentSubtask)
		else:
			# ensure that correct subtask is being done
			if self.currentSubtask != subtask:
				if self.currentSubtask is None or self.taskQueue is None:
					self.currentSubtask = subtask

				else:
					print("current:", self.currentSubtask, "subtask:", subtask)
					print(self.taskQueue)
					time.sleep(0.5)
					raise Exception("device already has different subtask!")

			debug.out("subtask specified: %s" % self.currentSubtask, 'b')

		if self.currentSubtask is None:
			debug.out("%s" % (self.batch))

		duration = None
		# do process and check if done
		if self.currentSubtask is not None:
			sim.debug.out("updating device %s %s %s" % (self, self.currentSubtask, self.getNumSubtasks()), 'r')
			affectedDevices, duration, devicePower = self.currentSubtask.update(visualiser) # only used in simple simulations
			# self.updatePreviousTimestamp(self.currentTime + duration)
			self.currentTime.increment(duration)
			debug.out("subtask %s time handled from %f to %f" % (self, self.previousTimestamp, self.currentTime.current), 'p')
			# print(affectedDevices, duration)
		else:
			# just idle, entire td is used
			self.currentTd = sim.simulations.constants.TD


		if affectedDevice is not None:
			affectedDevices += [affectedDevice]

		return affectedDevices, duration, devicePower

	def updatePreviousTimestamp(self, newTimestamp):
		if newTimestamp > self.previousTimestamp:
			self.previousTimestamp = newTimestamp
		debug.out("%s time handled to %f" % (self, self.previousTimestamp), 'p')



	# def timeOutSleep(self):
	# 	# check for idle sleep trigger
	# 	for component in self.components:
	# 		if isinstance(component, sim.devices.components.processor.processor):
	# 			component.timeOutSleep()

	# def updateSleepStatus(self, asleepBefore):
	# 	raise Exception("deprecated")
	# 	self.timeOutSleep()
	#
	# 	asleepAfter = self.asleep()
	#
	# 	if asleepBefore and asleepAfter:
	# 		warnings.warn("don't think this is correct")
	# 		self.totalSleepTime += self.currentTd

	def incremementTotalSleepTime(self, increment):
		self.totalSleepTime += increment

	def expectedLifetime(self):
		# estimate total life time based on previous use
		if self.averagePower == 0:
			return np.inf
		else:
			return self.energyLevel / self.averagePower

	def setCurrentBatch(self, job):
		if job.hardwareAccelerated:
			self.currentBatch = job.currentTask
		else:
			self.currentBatch = 0
		sim.debug.out("Setting current batch to {} ({})".format(self.currentBatch, job), 'b')
		# time.sleep(.5)

	def addJobToBatch(self, job):
		if job.hardwareAccelerated:
			task = job.currentTask
		else:
			# 0 task indicates software solutions
			task = 0

		# print("adding job to batch", self.batch)
		# create list if new task
		if task not in self.batch.keys():
			self.batch[task] = list()
		
		self.batch[task].append(job)


	def batchLengths(self):
		return [len(batch) for key, batch in self.batch.items()]

	def maxBatchLength(self):
		# investigate batch if not empty
		if self.batch:
			longestBatch = np.argmax([len(item) for key, item in self.batch.items()])
			return len(self.batch[list(self.batch.keys())[longestBatch]]), longestBatch
		else:
			return 0, 0

	def batchLength(self, task):
		# return batch length for a specific task
		if task in self.batch:
			return len(self.batch[task])
		else:
			sim.debug.out("batch {} does not exist".format(task))
			# print(self.batch)
			# print()
			return 0

	def isQueueFull(self, task):
		full = self.batchLength(task) >= self.maxJobs
		debug.out("jobs: %d full: %s" % (self.batchLength(task), full))
		return full

	def nextJobFromBatch(self):
		# print("currentjob", self.currentJob)
		if self.currentJob is None:
			# print([len(self.batch[batch]) > 0 for batch in self.batch])
			# if len(self.batch) > 0:
			# print ("keys", self.batch.keys())
			maxBatchLength, maxBatchIndex = self.maxBatchLength()
			# print('max batch', maxBatchLength, maxBatchLength)
			if maxBatchLength > 0:
				# check current batch
				if self.currentBatch is None:
					# batch first job in batch
					if self.batch.keys() is not None:
						self.currentBatch = list(self.batch.keys())[maxBatchIndex]
						# TODO: must keep going until all batches are empty
						sim.debug.out("starting batch {}".format(self.currentBatch))

				sim.debug.out("grabbed job from batch")
				# if self.currentBatch not in self.batch.keys():
				# 	print ("Batch does not exist in node", self.batch, self.currentBatch)
				self.currentJob = self.batch[self.currentBatch][0]
				self.removeJobFromBatch(self.currentJob)

				return self.currentJob
			else:
				sim.debug.out("No more jobs in batch", 'c')
				# self.batchProcessing = False
				self.currentJob = None
				self.currentBatch = None
		# else:
		# 	print("already has active job...")
		# 	return self.currentJob
		return None

	def removeJobFromBatch(self, job):
		sim.debug.out("batch before remove {}".format(self.batch))
		found = False
		# check if current batch exists
		if self.currentBatch is not None:
			if job in self.batch[self.currentBatch]:
				self.batch[self.currentBatch].remove(job)
				found = True
			else:
				raise Exception("Could not find job to remove from batch")
		# no batch exists
		else:
			# find job in all batches
			for key in self.batch:
				if job in self.batch[key]:
					self.batch[key].remove(job)
					found = True
					break

		assert found is True
		sim.debug.out("batch after remove {}".format(self.batch))

	def addJobToQueue(self, job):
		sim.debug.out("adding %s to queue of %s" % (job, self))
		self.jobQueue.put((job.id, job))

	def nextJob(self):
		# print("nextjob", self.currentJob, self.getNumJobs(), )
		if self.currentJob is None:
			if self.getNumJobs() > 0:
				index, self.currentJob = self.jobQueue.get()
				sim.debug.out("grabbed job from queue: %s (%d)" % (self.currentJob, self.getNumJobs()))
				# self.jobQueue.remove(self.currentJob)

				# see if it's a brand new job
				if not self.currentJob.started:
					affectedDevice, newSubtask = self.currentJob.start()
					affectedDevice.addSubtask(newSubtask) # add subtask from brand new job
					return affectedDevice, newSubtask
				else:
					assert self.getNumSubtasks() > 0
					sim.debug.out("\tALREADY STARTED")

		# no new jobs started
		return None

	def removeJob(self, job):
		sim.debug.out("REMOVE JOB FROM {}".format(self))
		# sim.debug.out ('{} {}'.format(self.jobQueue, job))
		# try to remove from queue (not there if from batch)
		# if job in self.jobQueue:
		# 	self.jobQueue.remove(job)
		# set as not current job
		if self.currentJob is job:
			# print("set job to NONE")
			self.currentJob = None

		sim.debug.out("resulting job: %s (%s)" % (self.currentJob, str(self.getNumSubtasks())))

	def checkGracefulFailure(self):
		if not self.gracefulFailure:
			if self.getEnergyLevelPercentage() <= self.gracefulFailureLevel:
				# print(self, "graceful failure", self.getEnergyLevelPercentage(), self.gracefulFailureLevel)
				self.performGracefulFailure()

	def performGracefulFailure(self):
		self.gracefulFailure = True
		# print(self.gracefulFailureLevel, self.getEnergyLevelPercentage())
		for dev in self.offloadingOptions: dev.removeOffloadingOption(self)

		# print("graceful failure with", self, self.batchLengths(), np.sum(self.batchLengths()))

	def hasOffloadingOptions(self):
		# print(self.offloadingOptions, len(self.offloadingOptions))
		return len(self.offloadingOptions) > 0

from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
	priority: int
	item: Any=field(compare=False)

	def __repr__(self): return "(%.2f - %s)" % (self.priority, self.item)