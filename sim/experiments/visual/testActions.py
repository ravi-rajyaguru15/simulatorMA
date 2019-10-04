import sim.constants
import sim.offloadingPolicy
import sim.systemState
import sim.offloadingDecision
import sim.job
import sim.counters
import sim.debug
from sim.simulation import simulation
import sys

sim.debug.enabled = False
sim.debug.learnEnabled = True

sim.constants.JOB_LIKELIHOOD = 0
sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
sim.constants.NUM_DEVICES = 2
sim.constants.DRAW_DEVICES = False
sim.constants.MINIMUM_BATCH = 1e10
sim.constants.PLOT_TD = sim.constants.TD * 10

exp = simulation(True)
sim.simulation.current = exp

exp.simulateTime(sim.constants.PLOT_TD * 1)
dev = exp.devices[0]
# time.sleep(1)

# fix decision to local
first = sim.job.job(dev, 5, hardwareAccelerated=True)
decision = sim.offloadingDecision.possibleActions[3]
decision.updateDevice(dev)
print("override first")
print("target index", decision.targetDeviceIndex)
print("target device", decision.targetDevice)
first.setDecisionTarget(decision)
dev.addJob(first)
exp.simulateUntilJobDone()
print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)
print("local done")

# fix decision to wait
second = sim.job.job(dev, 5, hardwareAccelerated=True)
decision = sim.offloadingDecision.possibleActions[2]
decision.updateDevice(dev)
print("target index", decision.targetDeviceIndex)
second.setDecisionTarget(decision)
dev.addJob(second)
exp.simulateTime(sim.constants.PLOT_TD * 100)
print("wait done")
print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)
# time.sleep(1)
# batch 1 


# offload from 1 to 0 then wait
print('\n\n\n\n\n')
sim.debug.out("THIRD", 'g')
dev2 = exp.devices[1]
third = sim.job.job(dev2, 5, hardwareAccelerated=True)
decision = sim.offloadingDecision.possibleActions[0]
decision.updateDevice(dev)
print("target index", decision.targetDeviceIndex)
third.setDecisionTarget(decision)
dev2.addJob(third)
print("offload 1 0")
while dev.currentJob is None:
	exp.simulateTick()
	print('\n\n-\n')
print("dev has job again")
print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)
decision = sim.offloadingDecision.possibleActions[2]
decision.updateDevice(dev)
third.setDecisionTarget(decision)

# time.sleep(1)
# batch 2
print("\n\nshould activate now...")
exp.simulateTick()
assert third.immediate == False

# offload from 0 to 1 to 0 then wait
print("\n\n\n\n\n")
sim.debug.out("FOURTH", 'g')
fourth = sim.job.job(dev, 5, hardwareAccelerated=True)
decision = sim.offloadingDecision.possibleActions[1]
decision.updateDevice(dev)
print("target index", decision.targetDeviceIndex)
fourth.setDecisionTarget(decision)
dev.addJob(fourth)
print("offload 0 1 0")
while dev2.currentJob is None:
	exp.simulateTick()
	print('\n\n-\n')
print("dev2 has job again")
print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)
decision = sim.offloadingDecision.possibleActions[0]
decision.updateDevice(dev)
fourth.setDecisionTarget(decision)
counter = 0
while dev.currentJob is None and counter < 10:
	counter += 1
	exp.simulateTick()
	print('\n\n-\n')

if counter >= 10:
	print("infiniteish loop!")
	sys.exit(0)
print('dev has job again')
print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)
decision = sim.offloadingDecision.possibleActions[2]
decision.updateDevice(dev)
fourth.setDecisionTarget(decision)
# time.sleep(1)
# batch 2
assert fourth.immediate == False
print("\n\nshould activate now...")
exp.simulateTick()

sim.debug.enabled = True


# offload from 0 to 0
fifth = sim.job.job(dev, 5, hardwareAccelerated=True)
decision = sim.offloadingDecision.possibleActions[0]
decision.updateDevice(dev)
fifth.setDecisionTarget(decision)
dev.addJob(fifth)
# batch 3 
print("offload 0 0")
print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)
exp.simulateTick()

# do nothing for a while
print("doing nothing")
for i in range(100):
	exp.simulateTick()
print("done doing nothing")

# another local to start things off
print("\n\nanother local to start ")
sixth = sim.job.job(dev, 5, hardwareAccelerated=True)
decision = sim.offloadingDecision.possibleActions[3]
decision.updateDevice(dev)
print("override sixth")
print("target index", decision.targetDeviceIndex)
print("target device", decision.targetDevice)
sixth.setDecisionTarget(decision)
dev.addJob(sixth)
exp.simulateUntilJobDone()
print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)
print("local done")

sys.exit(0)
while exp.completedJobs < 4:
	exp.simulateTick()


# exp.simulateUntilJobDone()
# exp.simulateUntilJobDone()
# exp.simulateUntilJobDone()
# time.sleep(1)

print("job done")
exp.simulateTime(sim.constants.PLOT_TD * 10)

