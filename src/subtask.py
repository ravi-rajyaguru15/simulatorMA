import constants
from mcu import mcu
from fpga import fpga

class subtask:
    totalDuration = None
    startTime = None
    progress = None
    finished = None

    energyCost = None

    # device where it's coming from and where it's going
    origin = destination = None

    def __init__(self, duration, origin, destination):
        # self.startTime = currentTime
        self.totalDuration = duration
        self.progress = 0
        self.finished = False

    def tick(self):
        self.progress += constants.TD

        # is it done?
        self.finished = self.progress >= self.totalDuration


class processing(subtask):
    def __init__(self, device, samples, processor=None):
        # print "MCU ONLY PROCESSING"
        duration = self.energyCost = 0

        if processor is None: processor = device.fpga

                    # res = result(latency=self.mcu.processingTime(task.samples), energy=self.mcu.activeEnergy(self.mcu.processingTime(task.samples)))
        if isinstance(processor, fpga):
            print "FPGA processing"
            
            # overhead for mcu-fpga communication
            # time = this.mcuToFpgaLatency()
            # res = result(latency=time, energy=this.mcuToFpgaEnergy(time))
            # # processing 
            # res += this.fpga.process(this.message.samples)
            
            duration = device.mcuToFpgaLatency(samples)
            self.energyCost = device.mcuToFpgaEnergy(duration)
        
        duration += processor.processingTime(samples)
        self.energyCost += processor.activeEnergy(duration)
            
        subtask.__init__(self, duration, device, device)
