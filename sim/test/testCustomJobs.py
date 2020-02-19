from sim import debug
from sim.simulations import constants
from sim.simulations.SimpleSimulation import SimpleSimulation, NEW_JOB, PROCESS_SUBTASK
from sim.tasks import subtask
from sim.tasks.job import job
from sim.tasks.subtask import reconfigureFPGA

debug.enabled = True
constants.NUM_DEVICES = 2
exp = SimpleSimulation(autoJobs=False)
exp.reset()
dev = exp.devices[0]
dev2 = exp.devices[1]

# queue manual jobs
firstJob = job(dev, 1, True)
firstJob.started = True
firstJob.active = True
firstJob.creator = dev
firstJob.processingNode = dev
firstJob.owner = dev
dev.currentJob = firstJob

# exp.queueTask(1, NEW_JOB, dev)

# queue subtasks
reconf = reconfigureFPGA(firstJob)
# exp.queueTask(0.999, PROCESS_SUBTASK, dev, subtask=reconf)

# queue offloaded task
secondJob = job(dev, 1, True)
secondJob.creator = dev
secondJob.owner = dev
secondJob.processingNode = dev2
dev.currentJob = secondJob
exp.processAffectedDevice(secondJob.activate())

print("tasks lined up:", exp.queue.qsize())
exp.printQueue()
print()

exp.simulateQueuedTasks(reset=False)
