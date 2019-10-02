import sim.constants
import sim.offloadingPolicy
import sim.systemState
import sim.offloadingDecision
import sim.job
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
print ("local done")

# fix decision to wait
second = sim.job.job(dev, 5, hardwareAccelerated=True)
decision = sim.offloadingDecision.possibleActions[2]
decision.updateDevice(dev)
print("target index", decision.targetDeviceIndex)
second.setDecisionTarget(decision)
dev.addJob(second)
exp.simulateTime(sim.constants.PLOT_TD * 100)
print ("wait done")
# time.sleep(1)
# batch 1 


sim.debug.enabled = True

# offload from 1 to 0 then wait
dev2 = exp.devices[1]
third = sim.job.job(dev2, 5, hardwareAccelerated=True)
decision = sim.offloadingDecision.possibleActions[0]
decision.updateDevice(dev)
print('\n\n\n\n\n')
print("target index", decision.targetDeviceIndex)
third.setDecisionTarget(decision)
dev2.addJob(third)
print ("offload 1 0")
while dev.currentJob is None:
	exp.simulateTick()
	print ('\n\n-\n')
print("dev has job again")
# exp.simulateTime(sim.constants.PLOT_TD * 100)

# time.sleep(1)
# batch 2
sys.exit(0)

# offload from 0 to 1 to 0 then wait

# offload from 0 to 0
fourth = sim.job.job(dev, 5, hardwareAccelerated=True)
decision = sim.offloadingDecision.possibleActions[0]
print('decision', decision)
if decision.local: decision.targetDeviceIndex = int(sim.systemState.current.getField('selfDeviceIndex')[0])
print("target index", decision.targetDeviceIndex)
selectedDevice = exp.devices[decision.targetDeviceIndex]
fourth.decision = decision
fourth.setprocessingNode(selectedDevice)
dev.addJob(fourth)
# batch 3 
print ("offload 0 0")
sim.debug.enabled = False

while exp.completedJobs < 4:
	exp.simulateTick()

# exp.simulateUntilJobDone()
# exp.simulateUntilJobDone()
# exp.simulateUntilJobDone()
# time.sleep(1)

print("job done")
exp.simulateTime(sim.constants.PLOT_TD * 10)

