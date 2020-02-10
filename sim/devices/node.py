import traceback
from queue import PriorityQueue

import sim.learning.offloadingDecision
import sim.tasks.subtask
import sim.simulations.constants
# from sim.job import job
import sim.tasks.job
from sim.devices.components.fpga import fpga
import sim.devices.components.processor
import sim.debug

import time
import numpy as np
import sim.learning.systemState as systemState


class node:
	# message = None
	decision = None
	jobQueue = None
	taskQueue = None
	currentJob = None
	# queuedTask = None # used in simple simulation
	previousTimestamp = None
	numJobs = None
	currentSubtask = None
	simulation = None
	index = None

	energyLevel = None
	totalEnergyCost = None
	averagePower = None
	powerCount = None
	totalSleepTime = None
	drawLocation = None

	platform = None
	components = None
	processors = None
	jobActive = None
	alwaysHardwareAccelerate = None

	batch = None
	currentBatch = None
	batchFull = None

	currentTime = None
	currentTd = None # amount of current TD that this node is busy

	# drawing
	rectangle = None
	location = None
	episodeFinished = None

	def __init__(self, clock, platform, index, components, episodeFinished, alwaysHardwareAccelerate=None):
		self.platform = platform

		self.decision = sim.learning.offloadingDecision.offloadingDecision(self, systemState.current)
		# self.simulation = simulation
		self.currentTime = clock

		# self.resultsQueue = queue
		self.index = index
		# self.nodeType = nodeType

		self.reset()

		self.drawLocation = (0,0)

		self.setComponents(components)
		self.episodeFinished = episodeFinished
		self.alwaysHardwareAccelerate = alwaysHardwareAccelerate

	def reset(self):
		self.previousTimestamp = 0
		self.jobQueue = PriorityQueue()
		self.taskQueue = PriorityQueue()
		sim.debug.out("jobqueue" + str(self.jobQueue))
		
		self.resetEnergyLevel()
		self.averagePower = 0.05
		self.powerCount = 0
		self.totalEnergyCost = 0
		self.totalSleepTime = 0
		self.jobActive = False
		self.numJobs = 0
		self.batch = dict()

	def resetEnergyLevel(self):
		self.energyLevel = node.convertEnergy(self.platform.BATTERY_SIZE, self.platform.BATTERY_VOLTAGE)

	def getEnergyLevel(self): return self.energyLevel

	def setComponents(self, components):
		if components is None:
			return
		self.components = components
		self.processors = [component for component in self.components if isinstance(component, sim.devices.components.processor.processor)]
		for processor in self.processors:
			processor.timeOutSleep()


	@staticmethod
	# convert mAh to Joule
	def convertEnergy(mah, voltage):
		return mah * voltage * 3.6


	def __repr__(self):
		return "<" + str(type(self)) + " " + str(self.index) + ">"

	# def setOptions(self, options):
		# self.setOffloadingDecisions(options)

	def setOffloadingDecisions(self, devices):
		self.decision.setOptions(devices)

	def getCurrentConfiguration(self):
		# default behaviour is to not have a configuration
		return 0

	def hasFpga(self):
		return np.any([isinstance(component, fpga) for component in self.processors])

	def getFpgaConfiguration(self):
		if self.hasFpga():
			# assuming maximum one fpga per device
			return self.fpga.currentConfig

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
		self.addSubtask(sim.tasks.subtask.newJob(job), appendLeft=True)

	# appends one job to the end of the task queue (used for queueing future tasks)
	def addSubtask(self, task, appendLeft=False):
		task.owner = self
		sim.debug.out("adding subtask %s %s" % (str(task), str(self)))

		# prioritised tasks without jobs (batchContinue mostly)
		taskPriority = task.job.id if task.job is not None else 0
		self.taskQueue.put(PrioritizedItem(taskPriority, task))
		# if appendLeft:
		# 	self.taskQueue.appendleft(task)
		# else:
		# 	self.taskQueue.append(task)

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
				sim.debug.out (str(self) + " NEXT TASK " + str(self.currentSubtask))

			else:
				# sim.debug.out("no next task")
				self.currentSubtask = None

	def getNumJobs(self):
		return self.jobQueue.qsize()

	def getNumSubtasks(self):
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

	def batchLengths(self):
		return [len(batch) for key, batch in self.batch.items()]

	# reconsider each job in batch, maybe start it. return which device (if any) is affected
	def reconsiderBatch(self):
		sim.debug.learnOut("deciding whether to continue batch ({}) or not".format(self.batchLengths()), 'b')
		# sim.debug.out("Batch before: {0}/{1}".format(self.batchLength(self.currentJob.currentTask), sim.constants.MINIMUM_BATCH), 'c')
		sim.debug.out("Batch lengths before: {}".format(self.batchLengths()), 'c')
		for batchName in self.batch:
			currentBatch = self.batch[batchName]
			for job in currentBatch:
				sim.debug.learnOut("considering job from batch".format(job))
				newChoice = self.decision.redecideDestination(job.currentTask, job, self)
				# print("updated", newChoice)
				# check if just batching
				if newChoice == sim.learning.offloadingDecision.BATCH or newChoice.offloadingToTarget(self.index):  # (isinstance(newChoice, sim.offloadingDecision.offloading) and newChoice.targetDeviceIndex == self.owner.index):
					sim.debug.learnOut("just batching again: {}".format(newChoice), 'p')
				else:
					# update destination
					sim.debug.learnOut("changing decision to {}".format(newChoice), 'p')
					job.setDecisionTarget(newChoice)

					# remove it from the batch
					self.removeJobFromBatch(job)
					self.currentJob = job
					return job.activate()

		sim.debug.out("Batch lengths after: {}".format(self.batchLengths()), 'c')
		return None
		# sim.debug.out("Batch after: {0}/{1}".format(self.currentJob.processingNode.batchLength(self.job.currentTask), sim.constants.MINIMUM_BATCH), 'c')

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
		incrementalEnergy = totalPower * self.currentTd
		self.totalEnergyCost += incrementalEnergy
		# TODO: assuming battery powered
		# print (incrementalEnergy)
		self.energyLevel -= incrementalEnergy
		return incrementalEnergy

	def getTotalPower(self):
		# calculate total power for all components
		totalPower = 0
		for component in self.components:
			# print("component", component, component.getPowerState())
			totalPower += component.power()

		return totalPower

	def updateAveragePower(self, power):
		self.powerCount += 1
		# 1/n
		# self.averagePower += 1.0 / self.powerCount * (power - self.averagePower) 
		# alpha
		self.averagePower += sim.simulations.constants.EXPECTED_LIFETIME_ALPHA * (power - self.averagePower)
		# sim.debug.out("average power: {}, {}".format(power, self.averagePower))

	def updateTime(self, visualiser=None):
		devicePower = 0
		# if no jobs available, perhaps generate one
		asleepBefore = self.asleep()

		# see if there's a job available
		if self.currentJob is None:
			# print(self, "next job")
			self.nextJob()
		# restarting existing job
		elif self.currentJob.started and not self.currentJob.active:
			sim.debug.out("restarting existing job", 'r')
			self.currentJob.activate()

		# check if there's something to be done now
		if self.currentSubtask is None:
			self.nextTask()

		affectedDevices = None
		duration = None
		# print("updating device", self, self.currentSubtask, self.getNumSubtasks())
		# do process and check if done
		if self.currentSubtask is not None:
			affectedDevices, duration, devicePower = self.currentSubtask.update(visualiser) # only used in simple simulations
			self.previousTimestamp = self.currentTime + duration
			# print(affectedDevices, duration)
		else:
			# just idle, entire td is used
			self.currentTd = sim.simulations.constants.TD

		self.updateSleepStatus(asleepBefore)

		return affectedDevices, duration, devicePower

	def updateSleepStatus(self, asleepBefore):
		# check for idle sleep trigger
		for component in self.components:
			if isinstance(component, sim.devices.components.processor.processor):
				component.timeOutSleep()

		asleepAfter = self.asleep()

		if asleepBefore and asleepAfter:
			self.totalSleepTime += sim.simulations.constants.TD

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

		# create list if new task
		if task not in self.batch.keys():
			self.batch[task] = list()
		
		self.batch[task].append(job)
	
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
			return 0

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
		if self.currentJob is None:
			if self.getNumJobs() > 0:
				index, self.currentJob = self.jobQueue.get()
				sim.debug.out("grabbed job from queue: %s (%d)" % (self.currentJob, self.getNumJobs()))
				# self.jobQueue.remove(self.currentJob)

				# see if it's a brand new job
				if not self.currentJob.started:
					return self.currentJob.start()
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

		sim.debug.out("resulting job: %s (%d)" % (self.currentJob, self.getNumSubtasks()))

from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
	priority: int
	item: Any=field(compare=False)

	def __repr__(self): return "(%.2f - %s)" % (self.priority, self.item)