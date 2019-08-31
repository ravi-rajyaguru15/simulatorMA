# TX RESULT destination swap source
import time 
import sys
import traceback

import sim.constants
from sim.mcu import mcu
from sim.fpga import fpga
from sim.powerState import powerStates
import sim.powerPolicy
import sim.offloadingPolicy
import sim.debug

class subtask:
	duration = None
	totalDuration = 0
	startTime = None
	delay = None
	progress = None
	owner = None

	started = None
	finished = None

	# energyCost = None

	# device that performed this subtask
	device = None

	job = None
	addsLatency = None
	# __name__ = "Unnamed Subtask"
	

	def __init__(self, job, duration, owner=None, addsLatency=True): #, energyCost): # , device): # , origin, destination):
		# self.startTime = currentTime

		# defined subtasks must first set duration and energy
		self.job = job
		if owner is None and job is not None:
			self.owner = self.job.owner
		else:
			self.owner = owner
		# assert(self.owner is not None)
		self.duration = duration
		self.__class__.totalDuration += duration
		# self.energyCost = energyCost

		self.progress = 0
		self.delay = 0
		self.started = False
		self.finished = False

	def tick(self):
		# only proceed if already started 
		if not self.started:
			sim.debug.out ("{} possible? {}".format(self, self.possible()))
			if self.possible():
				self.beginTask()
				sim.debug.out ("begin {} {}".format(self, self.started))
			else:
				self.delay += sim.constants.TD
				# check for deadlock
				if isinstance(self, txMessage):
					if self.deadlock():
						# raise Exception("DEADLOCK", self.job.creator, self.job.processingNode, sim.constants.OFFLOADING_POLICY, sim.constants.JOB_LIKELIHOOD)
						sim.debug.out("TX DEADLOCK!\n\n\n")
						# time.sleep(1.5)
						sim.debug.out ("removing task {} from {}".format(self.correspondingRx, self.destination))
						# resolve deadlock by making destination prioritise reception
						# move current task to queue to be done later
						try:
							self.destination.currentTask.delay = 0
							self.destination.addTask(self.destination.currentTask) # current task not None so nextTask won't start this task again
							self.destination.removeTask(self.correspondingRx)
							self.destination.currentTask = self.correspondingRx # must remove task before setting as current
							# self.destination.currentTask.start() # start to ensure it doesn't get removed
							# forced to be ready now
							self.beginTask()

						except ValueError:
							print()
							print("Cannot resolve deadlock!")
							print("current", self.destination.currentTask)
							print("duration", self.duration, self.correspondingRx.duration)
							print("rx", self.correspondingRx, self.correspondingRx.started)
							print("queue", self.destination.taskQueue)
							traceback.print_exc()
							sys.exit(0)
				elif isinstance(self, rxMessage):
					if self.deadlock():
						# raise Exception("DEADLOCK", self.job.creator, self.job.processingNode, sim.constants.OFFLOADING_POLICY, sim.constants.JOB_LIKELIHOOD)
						sim.debug.out("RX DEADLOCK!\n\n\n")
						if sim.debug.enabled: 
							time.sleep(1.5)
						# sim.debug.out ("removing task {} from {}".format(self.correspondingRx, self.destination))
						# resolve deadlock by making destination prioritise reception
						# move current task to queue to be done later
						try:
							self.source.currentTask.delay = 0
							self.source.addTask(self.source.currentTask) # current task not None so nextTask won't start this task again
							self.source.removeTask(self.correspondingTx)
							self.source.currentTask = self.correspondingTx # must remove task before setting as current
						except ValueError:
							print()
							print("Cannot resolve deadlock!")
							print("current", self.destination.currentTask)
							print("duration", self.duration, self.correspondingTx.duration)
							print("rx", self.correspondingTx, self.correspondingTx.started)
							print("queue", self.destination.taskQueue)
							traceback.print_exc()
							sys.exit(0)

					# # is it delayed?
					# elif self.delay >= sim.constants.MAX_DELAY:
					# 	print("task delayed!\n\n")
					# 	time.sleep(.1)
					# 	self.owner.swapTask()
					# 	# see if it's been swapped
					# 	if self.owner.currentTask != self:
					# 		self.delay = 0


				sim.debug.out("try again...")

				
		# print ("current task " + str(self.owner.currentTask))
		# progress task if it's been started
		if self.started:
			self.progress += sim.constants.TD

			# is it done?
			self.finished = self.progress >= self.duration

			# print (self, self.finished, self.progress, self.duration)

			# add any new tasks 
			if self.finished:
				# finish current task
				self.finishTask()

				# add delay to job
				if self.addsLatency:
					self.job.totalLatency += self.progress
				
				# # remove from owner
				# sim.debug.out("removing from tick")
				# self.owner.removeTask(self) removing when starting at least 
				self.owner.nextTask()

				# print ("current task " + str(self.owner.currentTask))
				# print (str(self.owner))

	def __str__(self):
		return self.__repr__()

		
	def __repr__(self):
		return "{} ({:.3f})".format(self.__name__, self.duration - self.progress)


	# default possible function is always available
	def possible(self):
		return True
	def deadlock(self):
		return False

	def finishTask(self):
		# pass
		# TODO: not setting currentTask to None
		sim.debug.out("finishing subtask!", 'b')

		self.owner.currentTask = None

		sim.debug.out("current task: {} {}".format(self.owner, self.owner.currentTask))
	
	def beginTask(self):
		# all versions of begin must set started
		self.start()
		# sim.debug.out("started {} {}".format(self, self.job.samples))
		sim.debug.out("started {}".format(self))
		pass

	def start(self):
		self.started = True

class createMessage(subtask):
	wirelessDuration = None
	__name__ = "Create Message"
	# destination = None
	# samples = None

	def __init__(self, job):
		sim.debug.out ("created createMessage")
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
		self.job.creator.mcu.idle()
		self.job.creator.addTask(txJob(self.job, self.job.creator, self.job.processingNode), appendLeft=True)

		subtask.finishTask(self)

# class idle(subtask):
# 	__name__ = "Idle"

# 	def beginTask(self):


class batchContinue(subtask):
	__name__ = "Batch Continue"

	def __init__(self, job):
		duration = job.processingNode.platform.MCU_BATCHING_LATENCY.gen()

		sim.debug.out("creating batchContinue with job {}".format(job))

		subtask.__init__(self, job, duration)

	def beginTask(self):
		subtask.beginTask(self)
		
	def finishTask(self):
		# # remove existing task from processing batch
		# self.job.processingNode.removeJobFromBatch(self.job)

# 		raise Exception(Traceback (most recent call last):
#   File "sim/experiments/experiment.py", line 382, in <module>
#     randomJobs(offloadingPolicy=sim.offloadingPolicy.ANYTHING, hw=True)
#   File "sim/experiments/experiment.py", line 200, in randomJobs
#     exp.simulate() #UntilTime(1)
#   File "/home/alwynster/git/simulator/sim/simulation.py", line 78, in simulate
#     self.simulateTick()
#   File "/home/alwynster/git/simulator/sim/simulation.py", line 145, in simulateTick
#     dev.updateTime(self.time)
#   File "/home/alwynster/git/simulator/sim/node.py", line 211, in updateTime
#     self.currentTask.tick()
#   File "/home/alwynster/git/simulator/sim/subtask.py", line 109, in tick
#     self.finishTask()
#   File "/home/alwynster/git/simulator/sim/subtask.py", line 204, in finishTask
#     processingMcu, processingFpga = self.job.processingNode.mcu, self.job.processingNode.fpga
# AttributeError: 'NoneType' object has no attribute 'processingNode')

		# check if there's more tasks in the current batch
		processingMcu, processingFpga = self.job.processingNode.mcu, self.job.processingNode.fpga
		# delete existing job to force next being loaded
		self.job.processingNode.currentJob = None
		self.job = self.job.processingNode.nextJobFromBatch()
		
		sim.debug.out ("next job from batch {}".format(self.job))
		# is there a new job?
		if self.job is None:
			# no more jobs available
			processingMcu.sleep()
			# # maybe sleep FPGA
			# sim.debug.out(sim.constants.FPGA_POWER_PLAN)

			# if sim.constants.FPGA_POWER_PLAN != sim.powerPolicy.STAYS_ON:
			# 	processingFpga.sleep()
			# 	sim.debug.out ("SLEEPING FPGA")
		else:
			self.job.processingNode.mcu.active()
			self.job.processingNode.addTask(newJob(self.job), appendLeft=True)
		
		subtask.finishTask(self)



class batching(subtask):
	__name__ = "Batching"
	
	def __init__(self, job):
		duration = job.processingNode.platform.MCU_BATCHING_LATENCY.gen()
		# energyCost = job.processingNode.energy(duration)
	
		subtask.__init__(self, job, duration) 

	def beginTask(self):
		self.job.processingNode.mcu.active()


		subtask.beginTask(self)

	def finishTask(self):
		# special case: hardware acceleration already there
		if self.job.hardwareAccelerated and self.job.processingNode.fpga.isConfigured(self.job.currentTask):
			self.job.processingNode.addTask(newJob(self.job), appendLeft=True)
		else:			
			# add current job to node's batch
			self.job.processingNode.addJobToBatch(self.job)
			# job has been backed up in batch and will be selected in finish
			self.job.processingNode.removeJob(self.job)

			sim.debug.out("Batch: {0}/{1}".format(self.job.processingNode.maxBatchLength(), sim.constants.MINIMUM_BATCH), 'c')

			# see if batch is full enough to start now
			if self.job.processingNode.maxBatchLength() >= sim.constants.MINIMUM_BATCH:
				self.job.processingNode.setCurrentBatch(self.job)

				# grab first task
				sim.debug.out("activating job")
				self.job.processingNode.currentJob = None
				self.job = self.job.processingNode.nextJobFromBatch()
				
				# start first job in queupe
				self.job.processingNode.addTask(newJob(self.job), appendLeft=True)
			# go to sleep until next task
			else:
				self.job.processingNode.mcu.sleep()
				# remove job from current owner
				# self.job.processingNode.removeJob(self.job)

		subtask.finishTask(self)


	# 	self.job.processingNode.fpga.idle()
	# 	self.job.processingNode.fpga.reconfigure(self.job.currentTask)

	# 	# move onto processing steps
	# 	self.job.processingNode.switchTask(mcuFpgaOffload(self.job))

class newJob(subtask):
	__name__ = "New Job"

	def __init__(self, job):
		duration = job.processingNode.platform.MCU_BATCHING_LATENCY.gen() # immediately move on (if possible)
	
		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.job.processingNode.mcu.active()

		subtask.beginTask(self)

	def finishTask(self):
		# start first job in queue
		if self.job.hardwareAccelerated:
			if self.job.processingNode.fpga.isConfigured(self.job.currentTask):
				self.job.processingNode.addTask(mcuFpgaOffload(self.job), appendLeft=True)
			else:
				self.job.processingNode.addTask(reconfigureFPGA(self.job), appendLeft=True)
		else:
			self.job.processingNode.addTask(processing(self.job), appendLeft=True)	
		
		subtask.finishTask(self)


class reconfigureFPGA(subtask):
	__name__ = "Reconfigure FPGA"
	
	def __init__(self, job): #  device, samples, processor=None):
		duration = job.processingNode.platform.RECONFIGURATION_TIME.gen()
		# energyCost = job.processingNode.reconfigurationEnergy(duration)
	
		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.job.processingNode.fpga.reconfigure(self.job.currentTask)
		# self.job.processingNode.jobActive = True
		subtask.beginTask(self)

	def finishTask(self):
		sim.debug.out("done reconfiguration")
		self.job.processingNode.fpga.idle()
		
		# move onto processing steps
		self.job.processingNode.addTask(mcuFpgaOffload(self.job), appendLeft=True)
	
		subtask.finishTask(self)


class xmem(subtask):
	# __name__ = "MCU FPGA Offload"
	
	def __init__(self, job): #  device, samples, processor=None):
		sim.debug.out ("created mcu fpga offloading task")
		
		duration = job.processingNode.mcuToFpgaLatency(job.datasize)
		# energyCost = job.processingNode.mcuToFpgaEnergy(duration)
	
		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.job.processingNode.mcu.active()
		self.job.processingNode.fpga.active()
		subtask.beginTask(self)

	def finishTask(self):
		self.job.processingNode.mcu.idle()
		self.job.processingNode.fpga.idle()
	
		subtask.finishTask(self)

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
		self.job.processingNode.addTask(processing(self.job), appendLeft=True)

		xmem.finishTask(self)

class fpgaMcuOffload(xmem):
	__name__ = "FPGA->MCU Offload"

	def finishTask(self):
		# check if offloaded
		if self.job.offloaded():
			self.job.processingNode.addTask(txResult(self.job, self.job.processingNode, self.job.creator), appendLeft=True)
		else:
			self.job.processingNode.addTask(batchContinue(self.job), appendLeft=True)
			# self.job.finish()
	
		xmem.finishTask(self)

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
	def __init__(self, job): #  device, samples, processor=None):
		# self.processor = processor

		sim.debug.out ("created processing task")
		
		duration = job.processor.processingTime(job.samples, job.currentTask)
		# energyCost = job.processingNode.processingEnergy(duration)

		# reduce message size
		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.job.processor.active()
		# if not self.job.offloaded():
		# 	self.job.creator.jobActive = True
		subtask.beginTask(self)

	def finishTask(self):
		self.job.processor.idle()

		sim.debug.out ("creating return message")

		self.job.processed = True	
		presize = self.job.datasize
		self.job.datasize = self.job.processedMessageSize()
		sim.debug.out ("datasize changed from {0} to {1}".format(presize, self.job.datasize))

		sim.debug.out("processed hw: {0} offload: {1}".format(self.job.hardwareAccelerated, self.job.offloaded()))
			
		if self.job.hardwareAccelerated:
			self.job.processingNode.addTask(fpgaMcuOffload(self.job), appendLeft=True)
		else:
			# check if offloaded
			if self.job.offloaded():
				self.job.processingNode.addTask(txResult(self.job, self.job.processingNode, self.job.creator), appendLeft=True)
			else:
				self.job.processingNode.addTask(batchContinue(self.job), appendLeft=True)
	
				
				# self.job.creator.jobActive = False
		subtask.finishTask(self)

class txMessage(subtask):
	destination = None
	source = None
	waitingForRX = None
	# messageSize = None
	# __name__ = "TX Message"
	
	def __repr__(self):
		return "{} (waiting for {})".format(self.__name__, self.destination) if not self.started else subtask.__repr__(self)

	def __init__(self, job, source, destination, jobToAdd):
		sim.debug.out("created txMessage")

		self.source = source
		self.destination = destination

		sim.debug.out("txmessage {} -> {}".format(source, destination))
		
		# source mcu does the work
		duration = job.creator.mrf.rxtxLatency(job.datasize)
		# energyCost = job.creator.mrf.txEnergy(duration)
		
		# create receiving task
		rx = jobToAdd(job, duration, self, source, destination) #, owner=destination)
		destination.addTask(rx)
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
		if isinstance(self.destination.currentTask, rxMessage):
			isPossible = self.destination.currentTask.correspondingTx == self
		
		# check if rxmessage is already started (done) TODO: why so quick?
		if self.correspondingRx.started:
			sim.debug.out("RX ALREADY STARTED OOPS")
			isPossible = True
		
		# if not possible, wait more, otherwise no more waiting
		self.waitingForRX = not isPossible

		# print ("TX message possible?\t{} {} {} {} {}".format(self.owner, self, self.correspondingRx.owner, self.destination.currentTask, isPossible))
		# print ("check1 {}".format(isinstance(self.destination.currentTask, rxMessage)))
		# try:
		# 	print ("check2 {}".format(self.destination.currentTask.correspondingTx))
		# 	print ("RX side: {} {}".foramt(self.destination, self.destination.currentTask.correspondingTx))
		# except:
			# print ("COULDN'T FIND DESTINATION TX")

		return isPossible
	
	# check if this task is being deadlocked
	def deadlock(self):
		# is destination also trying to send or receive?
		if isinstance(self.destination.currentTask, txMessage) or isinstance(self.destination.currentTask, rxMessage):
			# is it not started
			if not self.started and not self.destination.currentTask.started:
				# is it also trying to send 
				

				# is it trying to send to me?
				# if (self.destination is self.destination.currentTask.source) and (self.source is self.destination.currentTask.destination):
				return True
		# any other case is 
		return False

		# # return not self.job.creator.mrf.busy and not self.job.processingNode.mrf.busy
		# sim.debug.out ("possible? {} {} {}".format(self.source.mrf.busy(), self.destination.mrf.busy(), self.destination.mcu.isIdle()))
		# # when checking if possible, already switch to idle
		# possible = not self.source.mrf.busy() and not self.destination.mrf.busy() and not self.destination.mcu.isIdle()
		# if not possible: self.source.mrf.idle()
		# return possible
	
	# start new job
	def beginTask(self):
		self.source.mrf.tx()
		# self.destination.mrf.rx()
		# TODO: check these in the experiments
		self.source.mcu.idle()
		# self.destination.mcu.idle()

		# also start rx task, to ensure that it stays active
		self.correspondingRx.start()

		subtask.beginTask(self)
	
	def finishTask(self):
		self.source.mrf.sleep()
		self.source.mcu.sleep()
		# self.destination.mrf.sleep()

		subtask.finishTask(self)


	
class txJob(txMessage):
	__name__ = "TX Job"
	
	def __init__(self, job, source, destination):
		# add receive task to destination
		sim.debug.out("adding TX job")
		# destination.switchTask((self.job, self.duration, self, owner=self.destination))

		txMessage.__init__(self, job, source, destination, jobToAdd=rxJob)

	# def beginTask(self):
	# 	if self.destination.currentTask is not None:
	# 		print("job {} {}".format(self.destination, self.destination.currentTask))
	# 		raise Exception("Cannot start RX task in {} from {}".format(self.source,self.destination))
		
	# 	# self.destination.switchTask(rxJob(self.job, self.duration))

	# 	txMessage.beginTask(self)

	def finishTask(self):
		# if offloading, this is before processing
		# if not self.job.processed:
		# move job to new owner
		sim.debug.out ("moving job to processingNode")
		# move job to the processing from the creator 
		newOwner = self.job.processingNode		
		# self.job.creator.waiting = True

		self.job.moveTo(newOwner)

		# # after offloading job, no task 
		# self.owner.currentTask = None

		txMessage.finishTask(self)


class txResult(txMessage):
	__name__ = "TX Result"
	
	def __init__(self, job, source, destination):
		# add receive task to destination
		sim.debug.out("adding TX result")
		# destination.switchTask = rxResult(self.job, self.duration, self, owner=self.destination)

		txMessage.__init__(self, job, source, destination, jobToAdd=rxResult)

	def finishTask(self):
		# this is result being returned
		# self.job.processingNode.jobActive = False


		# see if there's a next job to continue
		self.job.processingNode.addTask(batchContinue(self.job), appendLeft=True)

		# move result of job back to the creator
		# self.job.moveTo(self.job.creator)
		txMessage.finishTask(self)

class rxMessage(subtask):
	correspondingTx = None
	source, destination = None, None
	# __name__ = "RX Message"

	def __repr__(self):
		return "{} (waiting for {})".format(self.__name__, self.source) if not self.started else subtask.__repr__(self)
	
	def __init__(self, job, duration, correspondingTx, source, destination):
		self.source = source
		self.destination = destination
	# 	sim.debug.out ("created rxMessage")

	# 	# energyCost = job.processingNode.mrf.rxEnergy(duration)
		self.correspondingTx = correspondingTx

		subtask.__init__(self, job, duration, owner=destination)

		
	# only possible if the tx is waiting for it
	def possible(self):
		sim.debug.out("{} possible? corresponding TX: {} source task: {} current? {}".format(self, self.correspondingTx, self.source.currentTask, self.correspondingTx == self.source.currentTask))
		# start if tx is also waiting, otherwise if tx has started already
		return self.correspondingTx == self.source.currentTask or self.correspondingTx.started

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

	def finishTask(self):
		sim.debug.out ("mrf not busy anymore")
		# self.job.creator.mrf.sleep()
		self.owner.mrf.sleep()
		# self.job.processingNode.mrf.sleep()
		sim.debug.out("finishing rxmessage!", 'b')
	
		subtask.finishTask(self)

		# # destination receives 
		# receiveEnergyCost = destination.mcu.activeEnergy(this.mrf.rxtxLatency(this.message.size) destination.mrf.rxEnergy(messageSize)
		
		# subtask.__init__(self, duration, energyCost, source) # , device, device)

	# check if this task is being deadlocked
	def deadlock(self):
		# is source also trying to receive? sending takes presedence...
		if isinstance(self.source.currentTask, rxMessage):
			# is it not started
			if not self.started and not self.source.currentTask.started:
				return True
		# any other case is 
		return False


class rxJob(rxMessage):
	__name__ = "RX Job"
	
	def finishTask(self):
		sim.debug.out("adding processing task 1")
		# add this task to the right, so it doesn't happen soon
		self.job.processingNode.addTask(batching(self.job)) #, appendLeft=True)

		rxMessage.finishTask(self)

class rxResult(rxMessage):
	__name__ = "RX Result"

	def finishTask(self):
		sim.debug.out("\treceived offloaded result")
		self.job.finish()

		self.owner.mcu.sleep()
		# self.job.creator.waiting = False
		# self.job.creator.jobActive = False

		# self.owner.currentTask = None
		sim.debug.out("finishing rxresult!", 'b')

		rxMessage.finishTask(self)


# class receiving(subtask):
#     def __init__(self, device, messageSize):
#         # destination mcu
#         duration = device.processingTime(samples)
#         energyCost = device.mcu.activeEnergy(duration)
			
#         # reception latency does not add overhead
#         subtask.__init__(self, duration=0, energyCost=energyCost, device=destination) # , device, device)

#         print "MESSAGE SIZE NOT CHANGING"

	# def sendTo(this, destination):
	# 	latency = this.mcu.messageOverheadLatency.gen() + this.mrf.rxtxLatency(this.message.size)
	# 	energy = this.mcu.overheadEnergy() + this.mrf.txEnergy(this.message.size)

	# 	res = destination.receive(this.message)
	# 	this.message = None

	# 	return result(latency, energy) + res
	
	# def receive(this, message):
	# 	this.message = message;
	# 	# reception does not add latency
	# 	return result(latency=0, energy=this.mcu.activeEnergy(this.mrf.rxtxLatency(this.message.size) + this.mrf.rxEnergy(this.message.size)))

