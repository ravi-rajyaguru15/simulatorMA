import constants
from mcu import mcu
from fpga import fpga
from powerState import powerStates

class subtask:
	duration = None
	startTime = None
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
		if owner is None:
			self.owner = self.job.owner
		else:
			self.owner = owner
		self.duration = duration
		# self.energyCost = energyCost

		self.progress = 0
		self.started = False
		self.finished = False

	def tick(self):
		# only proceed if already started 
		if not self.started:
			if self.possible():
				self.beginTask()

		# only start td afterwards, in order to synchronise
		else:
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
					
				# remove from owner
				self.owner.removeTask(self)

	def __str__(self):
		return (self.__name__)

		
	def __repr__(self):
		return (self.__name__)


	# default possible function is always available
	def possible(self):
		return True

	def finishTask(self):
		pass
	
	def beginTask(self):
		# all versions of begin must set started
		self.started = True
		print ("started", self, self.job.samples)
		pass


class createMessage(subtask):
	wirelessDuration = None
	__name__ = "Create Message"
	# destination = None
	# samples = None

	def __init__(self, job):
		print ("created createMessage")
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
		self.job.creator.addTask(txMessage(self.job, self.job.creator, self.job.processingNode))



class batching(subtask):
	__name__ = "Batching"
	
	def __init__(self, job):
		duration = constants.TD # immediately move on (if possible)
		# energyCost = job.processingNode.energy(duration)
	
		subtask.__init__(self, job, duration) 

	def beginTask(self):
		# add current job to node's batch
		self.job.processingNode.batch.append(self.job)

		# see if batch is full enough to start now
		if len(self.job.processingNode.batch) >= constants.MINIMUM_BATCH:
			self.job.processingNode.batchProcessing = True
			
		# wait for another job
		self.job.processingNode.currentJob = None # job has been backed up in batch

		subtask.beginTask(self)

	def finishTask(self):
		if self.job.processingNode.batchProcessing:
			# start first job in queue
			firstJob = self.job.processingNode.batch
			self.job.processingNode
			if self.job.hardwareAccelerated:
				if self.job.processingNode.fpga.isConfigured(self.job.currentTask):
					self.job.processingNode.addTask(mcuFpgaOffload(self.job))
				else:
					self.job.processingNode.addTask(reconfigureFPGA(self.job))
			else:
				self.job.processingNode.addTask(processing(self.job))
	# 	self.job.processingNode.fpga.idle()
	# 	self.job.processingNode.fpga.reconfigure(self.job.currentTask)

	# 	# move onto processing steps
	# 	self.job.processingNode.addTask(mcuFpgaOffload(self.job))

class reconfigureFPGA(subtask):
	__name__ = "Reconfigure FPGA"
	
	def __init__(self, job): #  device, samples, processor=None):
		duration = constants.RECONFIGURATION_TIME.gen()
		# energyCost = job.processingNode.reconfigurationEnergy(duration)
	
		subtask.__init__(self, job, duration)

	def beginTask(self):
		self.job.processingNode.fpga.reconfigure(self.job.currentTask)
		# self.job.processingNode.jobActive = True
		subtask.beginTask(self)

	def finishTask(self):
		self.job.processingNode.fpga.idle()
		
		# move onto processing steps
		self.job.processingNode.addTask(mcuFpgaOffload(self.job))

class xmem(subtask):
	# __name__ = "MCU FPGA Offload"
	
	def __init__(self, job): #  device, samples, processor=None):
		print ("created mcu fpga offloading task")
		
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

		# if self.job.processed:
		# 		# check if offloaded
		# 	if self.job.offloaded():
		# 		self.job.processingNode.addTask(txMessage(self.job, self.job.processingNode, self.job.creator))
		# 	else:
		# 		self.job.finish()
		# 		# self.job.creator.jobActive = False

		# else:
		# 	# always follow up with processing
		# 	self.job.processingNode.addTask(processing(self.job))			
	
	# def possible(self):
	# 	if
	# 	# TODO: when offloaded, possible only if host not busy, 
	# 	# TODO: also only possible to start reconfigure if fpga and mcu isn't busy
class mcuFpgaOffload(xmem):
	__name__ = "MCU->FPGA Offload"

	def finishTask(self):
		# always follow up with processing
		self.job.processingNode.addTask(processing(self.job))

		xmem.finishTask(self)

class fpgaMcuOffload(xmem):
	__name__ = "FPGA->MCU Offload"

	def finishTask(self):
		# check if offloaded
		if self.job.offloaded():
			self.job.processingNode.addTask(txMessage(self.job, self.job.processingNode, self.job.creator))
		else:
			self.job.finish()
	
		xmem.finishTask(self)

	# def possible(self):
	# 	if
	# 	# TODO: when offloaded, possible only if host not busy, 
	# 	# TODO: also only possible to start reconfigure if fpga and mcu isn't busy

class processing(subtask):
	__name__ = "Processing"
	
	# processor = None
	def __init__(self, job): #  device, samples, processor=None):
		# self.processor = processor

		print ("created processing task")
		
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

		print ("creating return message")

		self.job.processed = True	
		presize = self.job.datasize
		self.job.datasize = self.job.processedMessageSize()
		print ("datasize changed from", presize, "to", self.job.datasize)


		if self.job.hardwareAccelerated:
			self.job.processingNode.addTask(fpgaMcuOffload(self.job))
		else:
			# check if offloaded
			if self.job.offloaded():
				self.job.processingNode.addTask(txMessage(self.job, self.job.processingNode, self.job.creator))
			else:
				self.job.finish()
				
				# self.job.creator.jobActive = False


		
	

class txMessage(subtask):
	destination = None
	source = None
	messageSize = None
	# __name__ = "TX Message"
	
	
	def __init__(self, job, source, destination):
		print ("created txMessage")

		self.source = source
		self.destination = destination
		
		# source mcu does the work
		duration = job.creator.mrf.rxtxLatency(job.datasize)
		# energyCost = job.creator.mrf.txEnergy(duration)
		
		subtask.__init__(self, job, duration)


	# only possible if both source and destination mrf are available
	def possible(self):
		# return not self.job.creator.mrf.busy and not self.job.processingNode.mrf.busy
		return not self.source.mrf.busy() and not self.destination.mrf.busy()
	
	# start new job
	def beginTask(self):
		self.source.mrf.active()
		self.destination.mrf.active()

		subtask.beginTask(self)
	
	def finishTask(self):
		self.source.mrf.idle()
		self.destination.mrf.idle()

	
class txJob(txMessage):
	__name__ = "TX Job"
	
	def beginTask(self):
		# add receive task to destination
		self.destination.addTask(rxJob(self.job, self.duration))

		txMessage.beginTask(self)

	def finishTask(self):
		# if offloading, this is before processing
		if not self.job.processed:
			# move job to new owner
			print ("moving job to processingNode")
			# move job to the processing from the creator 
			newOwner = self.job.processingNode		
			# self.job.creator.waiting = True



		self.job.moveTo(newOwner)


class txResult(txMessage):
	__name__ = "TX Result"
	
	def beginTask(self):
		# add receive task to destination
		self.destination.addTask(rxResult(self.job, self.duration))

		txMessage.beginTask(self)

	def finishTask(self):
		# this is result being returned
		# self.job.processingNode.jobActive = False

		# move result of job back to the creator
		self.job.moveTo(self.job.creator)
		txMessage.finishTask(self)

class rxMessage(subtask):
	# __name__ = "RX Message"
	
	def __init__(self, job, duration):
		print ("created rxMessage")

		# energyCost = job.processingNode.mrf.rxEnergy(duration)

		subtask.__init__(self, job, duration)

	# WHAT?
	# def beginTask(self):
	# 	# receiving offloaded task
	# 	if self.job.offloaded():
	# 		self.job.processingNode.jobActive = True
	# 	# else:

	# 	subtask.beginTask(self)

	def finishTask(self):
		print ("mrf not busy anymore")
		self.job.creator.mrf.idle()
		self.job.processingNode.mrf.idle()

		# # destination receives 
		# receiveEnergyCost = destination.mcu.activeEnergy(this.mrf.rxtxLatency(this.message.size) destination.mrf.rxEnergy(messageSize)
		
		# subtask.__init__(self, duration, energyCost, source) # , device, device)

def rxJob(rxMessage):
	__name__ = "RX Job"

	def finishTask(self):
		print("adding processing task 1")
		self.job.processingNode.addTask(batching(self.job))

		rxMessage.finishTask(self)

def rxResult(rxMessage):
	__name__ = "RX Result"

	def finishTask(self):
		print("\treceived offloaded result")
		self.job.finish()
		# self.job.creator.waiting = False
		# self.job.creator.jobActive = False

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

