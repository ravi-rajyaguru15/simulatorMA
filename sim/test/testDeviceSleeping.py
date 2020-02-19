from sim import debug
from sim.devices.components import powerPolicy
from sim.simulations import constants
from sim.simulations.SimpleSimulation import SimpleSimulation, NEW_JOB, PROCESS_SUBTASK, SLEEP_COMPONENT
from sim.tasks import subtask
from sim.tasks.job import job
from sim.tasks.subtask import reconfigureFPGA, batching, dummy

debug.enabled = True
constants.NUM_DEVICES = 1
constants.FPGA_IDLE_SLEEP = 1
constants.FPGA_POWER_PLAN = powerPolicy.IDLE_TIMEOUT
exp = SimpleSimulation(autoJobs=False)
exp.reset()
dev = exp.devices[0]

# dummy start
dummyJob = job(dev, 1, True)
initialTask = dummy(dummyJob, dev, True, True)
exp.queueTask(0, PROCESS_SUBTASK, dev, subtask=initialTask)

# dummy mcu
dummyJob2 = job(dev, 1, True)
secondTask = dummy(dummyJob, dev, True, False)
exp.queueTask(0.25, PROCESS_SUBTASK, dev, subtask=secondTask)

# early check
exp.queueTask(0.5, SLEEP_COMPONENT, dev)

print("tasks lined up:", exp.queue.qsize())
exp.printQueue()
print()

exp.simulateQueuedTasks(reset=False)
