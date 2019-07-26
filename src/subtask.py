import constants
from mcu import mcu
from fpga import fpga

class subtask:
    duration = None
    startTime = None
    progress = None

    started = None
    finished = None

    energyCost = None

    # device that performed this subtask
    device = None

    job = None

    def __init__(self, job, duration, energyCost): # , device): # , origin, destination):
        # self.startTime = currentTime

        # defined subtasks must first set duration and energy

        self.job = job
        self.duration = duration
        self.energyCost = energyCost

        self.progress = 0
        self.started = False
        self.finished = False
        # self.device = device

        print ("Created generic subtask", self)

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
                self.createFollowUpTasks()



    # default possible function
    def possible(self):
        return True

    def createFollowUpTasks(self):
        print ("default no follow ups...")
        pass
    
    def beginTask(self):
        # all versions of begin must set started
        self.started = True
        print ("default empty begin")
        pass


class createMessage(subtask):
    wirelessDuration = None
    # destination = None
    # samples = None

    def __init__(self, job):
        print ("created createMessage")
        # self.destination = job.destination
        # self.samples = job.samples

        duration = job.creator.mcu.messageOverheadLatency.gen()
        energyCost = job.creator.mcu.activeEnergy(duration)

        subtask.__init__(self, job, duration, energyCost)
    
    # must send message now 
    def createFollowUpTasks(self):
        self.job.creator.addTask(txMessage(self.job))



    
class processing(subtask):
    processor = None
    def __init__(self, job, processor): #  device, samples, processor=None):
        self.processor = processor

        print ("always FPGA processing")

        offloadingDuration = job.processor.mcuToFpgaLatency(job.samples)
        offloadingEnergyCost = job.processor.mcuToFpgaEnergy(offloadingDuration)
        
        processingDuration = job.processor.processingTime(job)
        processingEnergyCost = job.processor.processingEnergy(processingDuration)

        # reduce message size
      	# self.size = self.samples * constants.SAMPLE_PROCESSED_SIZE.gen()
        job.datasize = job.processedMessageSize()

        duration = offloadingDuration + processingDuration
        energyCost = offloadingEnergyCost + processingEnergyCost

        subtask.__init__(self, job, duration, energyCost) # , device, device)

    def beginTask(self):
        self.processor.busy = True
        subtask.beginTask(self)

class txMessage(subtask):
    destination = None
    messageSize = None
    
    def __init__(self, job):
        print ("created txMessage")
        # self.destination = destination
        # self.messageSize = messageSize

        # source mcu does the work
        duration = job.creator.mrf.rxtxLatency(job.datasize)
        energyCost = job.creator.mrf.txEnergy(duration)
        
        subtask.__init__(self, job, duration, energyCost)


    # only possible if both source and destination mrf are available
    def possible(self):
        return not self.job.creator.mrf.busy and not self.job.processor.mrf.busy
    
    # start new job
    def beginTask(self):
        self.started = True
        # add receive task to destination
        self.job.processor.addTask(rxMessage(self.job, self.duration))
        print ("mrf now busy")
        self.job.creator.mrf.busy = self.job.processor.mrf.busy = True



class rxMessage(subtask):
    def __init__(self, job, duration):
        print ("created rxMessage")

        energyCost = job.processor.mrf.rxEnergy(duration)

        subtask.__init__(self, job, duration, energyCost)

    def createFollowUpTasks(self):
        print ("mrf not busy anymore")
        self.job.creator.mrf.busy = self.job.processor.mrf.busy = False
        
        self.job.processor.addTask(processing(self.job))        
        # # destination receives 
        # receiveEnergyCost = destination.mcu.activeEnergy(this.mrf.rxtxLatency(this.message.size) destination.mrf.rxEnergy(messageSize)
        
        # subtask.__init__(self, duration, energyCost, source) # , device, device)

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

