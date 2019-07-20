import constants
from mcu import mcu

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
    def __init__(self, device, processor, samples):
        # print "MCU ONLY PROCESSING"
        if isinstance(processor, mcu):

            duration = processor.processingTime(samples)
            self.energyCost = processor.activeEnergy(duration)
            
            subtask.__init__(self, duration, device, device)
                    # res = result(latency=self.mcu.processingTime(task.samples), energy=self.mcu.activeEnergy(self.mcu.processingTime(task.samples)))
        else:
            print "FPGA processing"
    