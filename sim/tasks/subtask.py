# TX RESULT destination swap source
import sys
import time

from sim import debug, simulations
from sim.debug import learnOut
from sim.learning.action import OFFLOADING
from sim.offloading import offloadingPolicy
from sim.simulations import constants
import numpy as np

enableGracefulFailure = True


class subtask:
	duration = None
	totalDuration = 0
	startTime = None
	delay = None
	progress = None
	owner = None
	id = 0

	started = None
	finished = None

	# energyCost = None

	# device that performed this subtask
	device = None

	job = None
	addsLatency = None
	__name__ = "Unnamed Subtask"

	# stub for incremental updating
	update = None

	def __init__(self, job, duration, owner=None,
				 addsLatency=True):  # , energyCost): # , device): # , origin, destination):
		# self.startTime = currentTime

		# defined subtasks must first set duration and energy
		self.job = job
		if owner is None and job is not None:
			self.owner = self.job.owner
		else:
			self.owner = owner
		# assert(self.owner is not None)

		debug.out("subtask {} duration: {:.10f}".format(self.__name__, duration), 'y')

		assert duration >= 0
		self.duration = duration
		self.__class__.totalDuration += duration
		# self.energyCost = energyCost

		self.progress = 0
		self.delay = 0
		self.started = False
		self.finished = False

		subtask.id += 1
		self.id = subtask.id

	# perform task in its entirety
	def perform(self, visualiser=None):
		self.beginTask()
		subtaskPower = self.owner.getTotalPower()
		debug.out("process {} {} {}".format(self, self.started, self.duration))
		debug.out("power: %s" % subtaskPower, 'g')
		debug.out("states: {0}".format([comp.getPowerState() for comp in self.owner.components]), 'y')
		self.progress = self.duration

		# update visualiser if passed in
		if visualiser is not None:
			visualiser.update()

		self.finished = True
		# self.owner.currentTime.increment(self.duration)

		affectedDevices = self.__class__.finishTask(self)
		debug.out("affected by finishing subtask: %s" % str(affectedDevices))

		# add delay to job
		if self.addsLatency:
			self.job.totalLatency += self.progress
		#
		# self.owner.nextTask()

		return affectedDevices, self.duration, subtaskPower

	# incrementally perform a piece of this subtask
	def tick(self):
		# only proceed if already started 
		if not self.started:
			debug.out("{} possible? {}".format(self, self.possible()))
			if self.possible():
				self.beginTask()
				debug.out("begin {} {}".format(self, self.started))
		# else:
		# 	self.delay += sim.constants.TD
		# 	# check for deadlock
		# 	if isinstance(self, txMessage):
		# 		if self.deadlock():
		# 			# raise Exception("DEADLOCK", self.job.creator, self.job.processingNode, sim.constants.OFFLOADING_POLICY, sim.constants.JOB_LIKELIHOOD)
		# 			debug.out("TX DEADLOCK!\n\n\n")
		# 			# time.sleep(1.5)
		# 			debug.out ("removing task {} from {}".format(self.correspondingRx, self.destination))
		# 			# TODO: move this to private functions
		# 			# resolve deadlock by making destination prioritise reception
		# 			# move current task to queue to be done later
		# 			try:
		# 				self.destination.currentSubtask.delay = 0
		# 				self.destination.addSubtask(self.destination.currentSubtask) # current task not None so nextTask won't start this task again
		# 				self.destination.removeTask(self.correspondingRx)
		# 				self.destination.currentSubtask = self.correspondingRx # must remove task before setting as current
		# 				# self.destination.currentSubtask.start() # start to ensure it doesn't get removed
		# 				# forced to be ready now
		# 				self.beginTask()
		#
		# 			except ValueError:
		# 				print()
		# 				print("Cannot resolve deadlock!")
		# 				print("current", self.destination.currentSubtask)
		# 				print("duration", self.duration, self.correspondingRx.duration)
		# 				print("rx", self.correspondingRx, self.correspondingRx.started)
		# 				print("queue", self.destination.taskQueue)
		# 				traceback.print_exc()
		# 				sys.exit(0)
		# 	elif isinstance(self, rxMessage):
		# 		if self.deadlock():
		# 			# raise Exception("DEADLOCK", self.job.creator, self.job.processingNode, sim.constants.OFFLOADING_POLICY, sim.constants.JOB_LIKELIHOOD)
		# 			debug.out("RX DEADLOCK!\n\n\n")
		# 			if debug.enabled:
		# 				time.sleep(1.5)
		# 			# debug.out ("removing task {} from {}".format(self.correspondingRx, self.destination))
		# 			# resolve deadlock by making destination prioritise reception
		# 			# move current task to queue to be done later
		# 			try:
		# 				self.source.currentSubtask.delay = 0
		# 				self.source.addSubtask(self.source.currentSubtask) # current task not None so nextTask won't start this task again
		# 				self.source.removeTask(self.correspondingTx)
		# 				self.source.currentSubtask = self.correspondingTx # must remove task before setting as current
		# 			except ValueError:
		# 				print()
		# 				print("Cannot resolve deadlock!")
		# 				print("current", self.destination.currentSubtask)
		# 				print("duration", self.duration, self.correspondingTx.duration)
		# 				print("rx", self.correspondingTx, self.correspondingTx.started)
		# 				print("queue", self.destination.taskQueue)
		# 				traceback.print_exc()
		# 				sys.exit(0)
		#
		# 		# # is it delayed?
		# 		# elif self.delay >= sim.constants.MAX_DELAY:
		# 		# 	print("task delayed!\n\n")
		# 		# 	time.sleep(.1)
		# 		# 	self.owner.swapTask()
		# 		# 	# see if it's been swapped
		# 		# 	if self.owner.currentSubtask != self:
		# 		# 		self.delay = 0
		#
		#
		# 	debug.out("try again...")

		totalDevicePower = self.owner.getTotalPower()

		# progress task if it's been started
		if self.started:
			# calculate progress in this tick
			remaining = self.duration - self.progress
			self.owner.currentTd = remaining if remaining < constants.TD else constants.TD

			self.progress += constants.TD

			# is it done?
			self.finished = self.progress >= self.duration

			# add any new tasks 
			if self.finished:
				# finish current task
				self.finishTask()

				# add delay to job
				if self.addsLatency:
					self.job.totalLatency += self.progress

				self.owner.nextTask()
		else:
			self.owner.currentTd = constants.TD

		# for compatibility with simple simulations
		return None, self.duration, totalDevicePower

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		return "{} [{}] ({:.3f})".format(self.__name__, self.job, self.duration - self.progress)

	# default possible function is always available
	def possible(self):
		return True

	def deadlock(self):
		return False

	def finishTask(self, affectedDevices):
		debug.out("finishing subtask! {} {}".format(self, self.owner), 'b')

		self.owner.currentSubtask = None

		if not isinstance(affectedDevices, list):
			affectedDevices = [affectedDevices]

		# add any new subtasks
		# TODO: add queuedTime to created subtasks
		if affectedDevices is not None:
			for affected in affectedDevices:
				if affected is not None:
					device, newSubtask = affected
					device.addSubtask(newSubtask)

		# debug.out("current task: {} {}".format(self.owner, self.owner.currentSubtask))
		return affectedDevices

	def beginTask(self):
		if (self.owner.currentJob is not None and self.job is None):
			debug.out("changing current job of %s from %s to %s" % (self.owner, self.owner.currentJob, self.job))
		# assert not (self.owner.currentJob is not None and self.job is None) # this would erase existing job
		self.owner.currentJob = self.job
		# all versions of begin must set started
		self.start()
		# debug.out("started {} {}".format(self, self.job.samples))
		debug.out("started {}".format(self))
		pass

	def start(self):
		self.started = True


class createMessage(subtask):
	wirelessDuration = None
	__name__ = "Create Message"

	# destination = None
	# samples = None

	def __init__(self, job):
		debug.out("created createMessage")
		# self.destination = job.destination
		# self.samples = job.samples

		duration = job.creator.mcu.messageOverheadLatency.gen()
		# energyCost = job.creator.mcu.activeEnergy(duration)

		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.job.creator.mcu.active()
		# self.job.creator.mcu.busy = True
		# self.job.creator.jobActive = True
		subtask.beginTask(self)

	# must send message now 
	def finishTask(self):
		self.owner.mcu.idle()

		newSubtask = txJob(self.job, self.job.owner, self.job.processingNode)
		return subtask.finishTask(self,
								  [(self.owner, newSubtask), (self.job.processingNode, newSubtask.correspondingRx)])


# class idle(subtask):
# 	__name__ = "Idle"

# 	def beginTask(self):


class batchContinue(subtask):
	__name__ = "Batch Continue"
	processingNode = None
	batch = None

	# job in parameter so
	def __init__(self, job=None, node=None):

		if node is not None:
			debug.out("creating batchContinue with node {}".format(node))
			self.processingNode = node
			self.job = job
		elif job is not None:
			debug.out("creating batchContinue with job {}".format(job))
			self.processingNode = job.processingNode
		else:
			raise Exception("Cannot create batchContinue without job and node")
		duration = self.processingNode.platform.MCU_BATCHING_LATENCY.gen()
		self.batch = self.processingNode.currentBatch

		subtask.__init__(self, job, duration)

	# def beginTask(self):
	# 	subtask.beginTask(self)

	def finishTask(self):
		# # remove existing task from processing batch
		# self.job.processingNode.removeJobFromBatch(self.job)
		# affected = None
		# newSubtask = None
		#
		# # if constants.OFFLOADING_POLICY == offloadingPolicy.REINFORCEMENT_LEARNING:
		# sleepMcu = False
		# if self.owner.reconsiderBatches:
		# 	affected = self.owner.reconsiderBatch()
		# 	if affected is None:
		# 		sleepMcu = True
		# else:
			# if doing entire

		# keep link to job in case we have to train on it
		currentJob = self.job

		# job is none if it's been sent to someone else (training in tx)
		if self.owner.reconsiderBatches and self.job is not None:
			# always trains once you decide
			self.owner.agent.train(self.job.currentTask, self.job, self.owner, cause=self.__name__)

		# reconsider batch inside continue function
		affected = self.processingNode.continueBatch(self.job)
		# print("batch continue:", affected, self.owner.currentJob)

		if not self.owner.reconsiderBatches and affected is None:
			# end of batch, train
			# nextTask = None if  is None else self.job.currentTask
			# as far as i know this only happens in graceful failure
			# print(self.owner.gracefulFailure, currentJob)

			if self.owner.gracefulFailure and not self.owner.hasOffloadingOptions():
				self.owner.agent.train(currentJob.currentTask, currentJob, self.owner, cause=self.__name__)
				print("\n\n\n\n\t\t**** special occurance ***\n\n\n\n\n")
				time.sleep(1)
			# else:
			# 	if not(not self.owner.gracefulFailure or (self.owner.gracefulFailure and currentJob is None)):
			# 		print(self.processingNode.batch, self.processingNode.batchLength(self.processingNode.currentBatch), self.processingNode.currentBatch, currentJob.currentTask)
			# 	assert not self.owner.gracefulFailure or (self.owner.gracefulFailure and currentJob is None)

		if affected is None:
			# sleepMcu = True
			self.owner.mcu.sleep()
		# else:
		# 	affected = self.job.processingNode, newJob(self.job)

		# if sleepMcu:
		# else:
		# 	# check if there's more tasks in the current batch
		# 	# processingMcu, processingFpga = self.processingNode.mcu, self.processingNode.fpga
		# 	# delete existing job to force next being loaded
		# 	self.processingNode.currentJob = None
		# 	self.job = self.processingNode.nextJobFromBatch()
		#
		# 	debug.out("next job from batch {}".format(self.job))
		# 	newjob = self.job is not None
		#
		# 	# is there a new job?
		# 	if not newjob:
		# 		# no more jobs available
		# 		self.processingNode.mcu.sleep()
		# 		# # maybe sleep FPGA
		# 		# debug.out(constants.FPGA_POWER_PLAN)
		#
		# 		# if constants.FPGA_POWER_PLAN != powerPolicy.STAYS_ON:
		# 		# 	processingFpga.sleep()
		# 		# 	debug.out ("SLEEPING FPGA")
		# 	else:
		# 		affected = self.job.processingNode, newJob(self.job)

		return subtask.finishTask(self, [affected])


class batching(subtask):
	__name__ = "Batching"

	def __init__(self, job):
		duration = job.processingNode.platform.MCU_BATCHING_LATENCY.gen()
		# energyCost = job.processingNode.energy(duration)

		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.owner.mcu.active()

		subtask.beginTask(self)

	def finishTask(self):
		# which devices have additional tasks added?
		affected = None
		nextSubtask = None
		# add current job to node's batch
		self.job.processingNode.addJobToBatch(self.job)
		# # job has been backed up in batch and will be selected in finish
		self.job.processingNode.removeJob(self.job)

		# if constants.OFFLOADING_POLICY == offloadingPolicy.REINFORCEMENT_LEARNING:
		sleepMcu = False
		# if constants.RECONSIDER_BATCHES:
		# 	# decide which of the jobs in the batch should be started now
		# 	affected = self.owner.reconsiderBatch()
		# 	if affected is None:
		# 		sleepMcu = True
		# else:
		self.owner.agent.train(self.job.currentTask, self.job, self.owner, cause=self.__name__)
		# TODO: this makes it train before energy costs from batching subtask are considered
		sleepMcu = True

		if sleepMcu:
			self.owner.mcu.sleep()

		# else: TODO: used for rule-based systems
		# 	# special case: hardware acceleration already there
		# 	if self.job.hardwareAccelerated and self.job.processingNode.fpga.isConfigured(self.job.currentTask):
		# 		debug.out("special case batching: hw already available")
		#
		# 		affected = self.job.processingNode, self.job.processingNode.setActiveJob(self.job.processingNode.nextJobFromBatch())
		# 	else:
		# 		debug.out("Batch: {0}/{1}".format(self.job.processingNode.batchLength(self.job.currentTask), constants.MINIMUM_BATCH), 'c')
		#
		# 		# see if batch is full enough to start now, or
		# 		# if decided to start locally
		# 		if self.job.processingNode.batchLength(self.job.currentTask) >= constants.MINIMUM_BATCH:
		# 			newSubtask = self.job.processingNode.setActiveJob(self.job.processingNode.nextJobFromBatch())
		# 			if self.job is not None:
		# 				affected = self.job.processingNode, newSubtask
		# 		# go to sleep until next task
		# 		else:
		# 			self.job.processingNode.mcu.sleep()

		return subtask.finishTask(self, [affected])


class newJob(subtask):
	__name__ = "New Job"

	def __init__(self, job):
		duration = job.processingNode.platform.MCU_BATCHING_LATENCY.gen()  # immediately move on (if possible)

		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.job.processingNode.mcu.active()

		subtask.beginTask(self)

	def finishTask(self):
		newSubtask = None
		# start first job in queue
		self.job.processingNode.currentBatch = self.job.currentTask

		# consider graceful failure
		if enableGracefulFailure and not self.owner.gracefulFailure:
			# self.owner.performGracefulFailure()
			self.owner.checkGracefulFailure()

		# either fail or start processing new job
		if self.owner.gracefulFailure:
			learnOut("GRACEFUL FAILURE: %s" % self.owner)
			debug.out("GRACEFUL FAILURE on %s %s %s" % (self.owner, self.owner.offloadingOptions, self.owner.batch))
			# debug.infoOut("training from %s" % self.owner.agent.systemState.getStateDescription(self.job.beforeState))
			# debug.infoOut("training to   %s" % self.owner.agent.systemState.getStateDescription(
			# 	self.owner.agent.systemState.getIndex()))

			if not self.owner.hasOffloadingOptions():
				# cannot offload to anything and dying
				return None
			else:

				self.job.beforeState = self.owner.agent.systemState.getCurrentState(self.job.currentTask, self.job, self.owner) # .getIndex()
				choice = self.owner.agent.getAction(OFFLOADING)
				self.job.latestAction = self.owner.agent.getActionIndex(choice)

				debug.out("choice %s %s" % (choice, self.owner.agent.latestAction))
				choice.updateTargetDevice(self.owner, self.owner.offloadingOptions)
				debug.out("%s %s %s %s" % (choice.local, self.owner, self.owner.offloadingOptions, choice.targetDevice))

				affectedDevice = self.owner
				self.job.processingNode = choice.targetDevice
				newSubtask = createMessage(self.job)
				debug.out("spraying %s" % self.job)
				# self.owner.agent.train(self.job.currentTask, self.job, self.owner, cause="Graceful Failure")

			# TODO: train based on failed jobs here
		else:
			affectedDevice = self.job.processingNode

			if self.job.hardwareAccelerated:
				if self.job.processingNode.fpga.isConfigured(self.job.currentTask):
					newSubtask = mcuFpgaOffload(self.job)
				else:
					newSubtask = reconfigureFPGA(self.job)
			else:
				newSubtask = processing(self.job)

		assert newSubtask is not None

		return subtask.finishTask(self, [(affectedDevice, newSubtask)])


class reconfigureFPGA(subtask):
	__name__ = "Reconfigure FPGA"

	def __init__(self, job):  # device, samples, processor=None):
		duration = job.processingNode.platform.reconfigurationTime(job.currentTask)
		# energyCost = job.processingNode.reconfigurationEnergy(duration)

		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.job.processingNode.fpga.reconfigure(self.job.currentTask)
		# self.job.processingNode.jobActive = True
		subtask.beginTask(self)

	def finishTask(self):
		debug.out("done reconfiguration")
		self.job.processingNode.fpga.idle()

		# start processing
		return subtask.finishTask(self, (self.job.processingNode, mcuFpgaOffload(self.job)))


class xmem(subtask):
	# __name__ = "MCU FPGA Offload"

	def __init__(self, job):  # device, samples, processor=None):
		debug.out("created mcu fpga offloading task")

		duration = job.processingNode.mcuToFpgaLatency(job.datasize)
		# energyCost = job.processingNode.mcuToFpgaEnergy(duration)

		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.job.processingNode.mcu.active()
		self.job.processingNode.fpga.active()
		subtask.beginTask(self)

	def finishTask(self, affectedDevices):
		self.job.processingNode.mcu.idle()
		self.job.processingNode.fpga.idle()

		return subtask.finishTask(self, affectedDevices)

	# if self.job.processed:
	# 		# check if offloaded
	# 	if self.job.offloaded():
	# 		self.job.processingNode.switchTask(txMessage(self.job, self.job.processingNode, self.job.creator))
	# 	else:
	# 		self.job.finish()
	# 		# self.job.creator.jobActive = False

	# else:
	# 	# always follow up with processing
	# 	self.job.processingNode.switchTask(processing(self.job))

# def possible(self):
# 	if
# 	# TODO: when offloaded, possible only if host not busy,
# 	# TODO: also only possible to start reconfigure if fpga and mcu isn't busy


class mcuFpgaOffload(xmem):
	__name__ = "MCU->FPGA Offload"

	def finishTask(self):
		# always follow up with processing
		# self.job.processingNode.addSubtask(, appendLeft=True)

		return xmem.finishTask(self, (self.job.processingNode, processing(self.job)))


class fpgaMcuOffload(xmem):
	__name__ = "FPGA->MCU Offload"

	def finishTask(self):
		# check if offloaded
		if self.job.offloaded():
			# self.job.processingNode.addSubtask(, appendLeft=True)
			newSubtask = txResult(self.job, self.job.processingNode, self.job.creator)
		else:
			self.job.finish() # not training in job finish
			# self.job.processingNode.addSubtask(, appendLeft=True)
			newSubtask = batchContinue(node=self.owner, job=self.job)

		return xmem.finishTask(self, [(self.job.processingNode, newSubtask)])

# def possible(self):
# 	if
# 	# TODO: when offloaded, possible only if host not busy,
# 	# TODO: also only possible to start reconfigure if fpga and mcu isn't busy


class processing(subtask):
	# TODO: test local processing without HW acceleration?
	__name__ = "Processing"

	def __repr__(self):
		return "{} [{}]".format(subtask.__repr__(self), self.job.currentTask)

	# processor = None
	def __init__(self, job):  # device, samples, processor=None):
		# self.processor = processor

		debug.out("created processing task")

		duration = job.processor.processingTime(job.samples, job.currentTask)

		# reduce message size
		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.job.processor.active()

		self.job.batchSize = self.job.processingNode.batchLength(self.job.currentTask)

		# if not self.job.offloaded():
		# 	self.job.creator.jobActive = True
		subtask.beginTask(self)

	def finishTask(self):
		self.job.processor.idle()

		debug.out("creating return message")

		self.job.processed = True
		presize = self.job.datasize
		self.job.datasize = self.job.processedMessageSize()
		debug.out("datasize changed from {0} to {1}".format(presize, self.job.datasize))

		debug.out("processed hw: {0} offload: {1}".format(self.job.hardwareAccelerated, self.job.offloaded()))

		if self.job.hardwareAccelerated:
			newSubtask = fpgaMcuOffload(self.job)
		else:
			# check if offloaded
			if self.job.offloaded():
				newSubtask = txResult(self.job, self.job.processingNode, self.job.creator)
			else:
				self.owner.agent.train(self.job.currentTask, self.job, self.owner, cause=self.__name__)
				newSubtask = batchContinue(self.job)

			# self.job.creator.jobActive = False
		return subtask.finishTask(self, [(self.job.processingNode, newSubtask)])


class txMessage(subtask):
	destination = None
	source = None
	waitingForRX = None

	# messageSize = None
	# __name__ = "TX Message"

	def __repr__(self):
		return "{} [{}] (waiting for {})".format(self.__name__, self.job,
												 self.destination) if not self.started else subtask.__repr__(self)

	def __init__(self, job, source, destination, jobToAdd):
		debug.out("created txMessage")

		self.source = source
		self.destination = destination

		debug.out("txmessage {} -> {}".format(source, destination))

		# source mcu does the work
		duration = job.creator.mrf.rxtxLatency(job.datasize)
		# energyCost = job.creator.mrf.txEnergy(duration)

		# create receiving task
		rx = jobToAdd(job, duration, self, source, destination)  # , owner=destination)
		# # destination.addSubtask(rx)
		self.correspondingRx = rx
		self.waitingForRX = False

		subtask.__init__(self, job, duration)

	def waiting(self):
		return self.waitingForRX

	# only possible if both source and destination mrf are available
	def possible(self):
		# possible once receiving task is active on the destination
		# wait for receiver to be on the reception task
		isPossible = False
		if isinstance(self.destination.currentSubtask, rxMessage):
			isPossible = self.destination.currentSubtask.correspondingTx == self

		# check if rxmessage is already started (done) TODO: why so quick?
		if self.correspondingRx.started:
			debug.out("RX ALREADY STARTED OOPS")
			isPossible = True

		# if not possible, wait more, otherwise no more waiting
		self.waitingForRX = not isPossible

		# print ("TX message possible?\t{} {} {} {} {}".format(self.owner, self, self.correspondingRx.owner, self.destination.currentSubtask, isPossible))
		# print ("check1 {}".format(isinstance(self.destination.currentSubtask, rxMessage)))
		# try:
		# 	print ("check2 {}".format(self.destination.currentSubtask.correspondingTx))
		# 	print ("RX side: {} {}".foramt(self.destination, self.destination.currentSubtask.correspondingTx))
		# except:
		# print ("COULDN'T FIND DESTINATION TX")

		return isPossible

	# check if this task is being deadlocked
	def deadlock(self):
		# is destination also trying to send or receive?
		if isinstance(self.destination.currentSubtask, txMessage) or isinstance(self.destination.currentSubtask,
																				rxMessage):
			# is it not started
			if not self.started and not self.destination.currentSubtask.started:
				# is it also trying to send

				# is it trying to send to me?
				# if (self.destination is self.destination.currentSubtask.source) and (self.source is self.destination.currentSubtask.destination):
				return True
		# any other case is
		return False

	# # return not self.job.creator.mrf.busy and not self.job.processingNode.mrf.busy
	# debug.out ("possible? {} {} {}".format(self.source.mrf.busy(), self.destination.mrf.busy(), self.destination.mcu.isIdle()))
	# # when checking if possible, already switch to idle
	# possible = not self.source.mrf.busy() and not self.destination.mrf.busy() and not self.destination.mcu.isIdle()
	# if not possible: self.source.mrf.idle()
	# return possible

	# start new job
	def beginTask(self):
		self.source.mrf.tx()
		# TODO: check these in the experiments
		self.source.mcu.idle()
		# self.destination.mcu.idle()

		# also start rx task, to ensure that it stays active
		self.correspondingRx.start()

		subtask.beginTask(self)

	def finishTask(self, affectedDevices):
		self.source.mrf.sleep()

		self.source.mcu.sleep()
		# self.destination.mrf.sleep()

		# return subtask.finishTask(self, [self.source, self.destination])
		return subtask.finishTask(self, affectedDevices)


class txJob(txMessage):
	__name__ = "TX Job"

	def __init__(self, job, source, destination):
		# add receive task to destination
		debug.out("adding TX job from {} to {}".format(source, destination))
		assert source is not destination
		txMessage.__init__(self, job, source, destination, jobToAdd=rxJob)

	# def beginTask(self):
	#
	# 	txMessage.beginTask(self)

	def finishTask(self, affectedDevices=None):
		# if using rl, update model
		# must update when starting,
		# if constants.OFFLOADING_POLICY == offloadingPolicy.REINFORCEMENT_LEARNING:
		debug.out("training after offloading job")
		self.owner.agent.train(self.job.currentTask, self.job, self.owner, cause=self.__name__)

		# removing job from sender
		self.owner.removeJob(self.job)

		if self.owner.gracefulFailure:
			debug.out("continuing graceful failure")
			nextSubtask = batchContinue(node=self.owner, job=self.job)
			affectedDevices = [(self.owner, nextSubtask)]

		return txMessage.finishTask(self, affectedDevices)


class txResult(txMessage):
	__name__ = "TX Result"

	def __init__(self, job, source, destination):
		# add receive task to destination
		debug.out("adding TX result")
		# destination.switchTask = rxResult(self.job, self.duration, self, owner=self.destination)

		txMessage.__init__(self, job, source, destination, jobToAdd=rxResult)

	def finishTask(self):
		# see if there's a next job to continue
		# self.job.processingNode.addSubtask(, appendLeft=True)

		# move result of job back to the creator
		self.owner.agent.train(self.job.currentTask, self.job, self.owner, cause=self.__name__)
		return txMessage.finishTask(self, (self.job.processingNode, batchContinue(node=self.owner)))


class rxMessage(subtask):
	correspondingTx = None
	source, destination = None, None

	# __name__ = "RX Message"

	def __repr__(self):
		return "{} (waiting for {})".format(self.__name__, self.source) if not self.started else subtask.__repr__(self)

	def __init__(self, job, duration, correspondingTx, source, destination):
		self.source = source
		self.destination = destination
		# 	debug.out ("created rxMessage")

		# 	# energyCost = job.processingNode.mrf.rxEnergy(duration)
		self.correspondingTx = correspondingTx

		subtask.__init__(self, job, duration, owner=destination)

	# only possible if the tx is waiting for it
	def possible(self):
		debug.out("{} possible? corresponding TX: {} source task: {} current? {}".format(self, self.correspondingTx,
																						 self.source.currentSubtask,
																						 self.correspondingTx == self.source.currentSubtask))
		# start if tx is also waiting, otherwise if tx has started already
		return self.correspondingTx == self.source.currentSubtask or self.correspondingTx.started

	# WHAT?
	def beginTask(self):
		self.owner.mrf.rx()
		# 	self.
		# 	subtask.beginTask(self)
		# 	# receiving offloaded task
		# 	if self.job.o"f"floaded():
		# 		self.job.processingNode.jobActive = True
		# 	# else:

		subtask.beginTask(self)

	def finishTask(self, affectedDevices):
		debug.out("mrf not busy anymore")
		# self.job.creator.mrf.sleep()
		self.owner.mrf.sleep()
		# self.job.processingNode.mrf.sleep()
		debug.out("finishing rxmessage!", 'b')

		return subtask.finishTask(self, affectedDevices)

	# # destination receives
	# receiveEnergyCost = destination.mcu.activeEnergy(this.mrf.rxtxLatency(this.message.size) destination.mrf.rxEnergy(messageSize)

	# subtask.__init__(self, duration, energyCost, source) # , device, device)

	# check if this task is being deadlocked
	def deadlock(self):
		# is source also trying to receive? sending takes presedence...
		if isinstance(self.source.currentSubtask, rxMessage):
			# is it not started
			if not self.started and not self.source.currentSubtask.started:
				return True
		# any other case is
		return False


class rxJob(rxMessage):
	__name__ = "RX Job"

	def __repr__(self):
		return "{} [{}]".format(self.__name__, self.job)

	def finishTask(self):
		# usingReinforcementLearning = constants.OFFLOADING_POLICY == offloadingPolicy.REINFORCEMENT_LEARNING

		debug.out("adding processing task 1")

		# if offloading, this is before processing
		# if not self.job.processed:
		# move job to new owner
		debug.out("moving job to processingNode")
		# move job to the processing from the creator
		newOwner = self.job.processingNode
		# self.job.creator.waiting = True

		# if usingReinforcementLearning:
		# 	debug.learnOut("training before reevaluating")
		# 	debug.learnOut("backward before update")
		# 	# TODO: this the correct device?
		# 	self.owner.agent.train(self.job.currentTask, self.job, self.owner)
		# 	# systemState.current.update(self.job.currentTask, self.job, self.owner) # still old owner
		# 	# self.job.creator.decision.privateAgent.backward(self.job.reward(), self.job.finished)

		# TODO: rx job in tdsimulation likely broken because not adding received job to backlog (assuming subtask is created)
		self.job.moveTo(newOwner)

		# if using rl, reevalute decision
		# if usingReinforcementLearning:
		# print()
		debug.out("updating decision upon reception")
		debug.out("owner: {}".format(self.job.owner))
		# systemState.current.update(self.job.currentTask, self.job, self.job.owner)
		# debug.out("systemstate: {}".format(systemState.current))

		# # print("systemstate: {}".format(systemState.current))
		# choice = self.job.owner.decision.privateAgent.forward(self.job.owner)
		# print("choice: {}".format(choice))

		# self.job.setDecisionTarget(choice)
		# self.job.activate()

		choice = self.job.owner.agent.redecideDestination(self.job.currentTask, self.job, self.job.owner)
		debug.learnOut("redeciding choice %s" % choice)
		self.job.setDecisionTarget(choice)
		affected = self.job.activate()
		# warnings.warn("redecision isn't affected i think")
		# affected = choice.targetDevice
		# otherwise, just add it to the local batch
		# else:
		# 	affected = self.job.processingNode, batching(self.job)

		return rxMessage.finishTask(self, [affected])


class rxResult(rxMessage):
	__name__ = "RX Result"

	def finishTask(self):
		debug.out("\treceived offloaded result")
		self.job.finish()

		self.owner.mcu.sleep()

		debug.out("finishing rxresult!", 'b')

		return rxMessage.finishTask(self, None)


class dummy(subtask):
	# only used for testing
	__name__ = "Dummy"
	mcuActive = None
	fpgaActive = None

	def __init__(self, job, device, mcuActive, fpgaActive):
		subtask.__init__(self, job, owner=device, duration=0)

		self.mcuActive = mcuActive
		self.fpgaActive = fpgaActive

	def beginTask(self):
		if self.mcuActive:
			self.owner.mcu.active()
		if self.fpgaActive:
			self.owner.fpga.active()

		subtask.beginTask(self)

	def finishTask(self):
		if self.mcuActive:
			# self.owner.mcu.active()
			self.owner.mcu.sleep()
		if self.fpgaActive:
			# self.owner.fpga.active()
			self.owner.fpga.idle()

		return subtask.finishTask(self, [None])
