import sim.constants
import sim.offloadingPolicy
from sim.simulation import simulation
import time

sim.constants.JOB_LIKELIHOOD = 0
sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
sim.constants.NUM_DEVICES = 2
sim.constants.DRAW_DEVICES = True
sim.constants.MINIMUM_BATCH = 3

exp = simulation(True)

exp.simulateTime(sim.constants.PLOT_TD * 10)
dev = exp.devices[0]
time.sleep(1)

# fix decision to local
first = sim.job.job(exp.time, dev, 5, dev.decision, hardwareAccelerated=True)
sim.systemState.current.updateDevice(dev)
decision = sim.offloadingDecision.possibleActions[3]
if decision.local: decision.targetDeviceIndex = sim.systemState.current.selfDeviceIndex
selectedDevice = exp.devices[decision.targetDeviceIndex]
first.decision = decision	
first.setprocessingNode(selectedDevice)
dev.addJob(first)
exp.simulateUntilJobDone()
print ("local done")
time.sleep(1)

# fix decision to wait
second = sim.job.job(exp.time, dev, 5, dev.decision, hardwareAccelerated=True)
decision = sim.offloadingDecision.possibleActions[2]
if decision.local: decision.targetDeviceIndex = sim.systemState.current.selfDeviceIndex
second.decision = decision	
second.setprocessingNode(selectedDevice)
dev.addJob(second)
exp.simulateTime(sim.constants.PLOT_TD * 10)
print ("wait done")
time.sleep(1)
# batch 1 

# offload from 1 to 0
dev2 = exp.devices[1]
third = sim.job.job(exp.time, dev2, 5, dev2.decision, hardwareAccelerated=True)
sim.systemState.current.updateDevice(dev2)
decision = sim.offloadingDecision.possibleActions[0]
if decision.local: decision.targetDeviceIndex = sim.systemState.current.selfDeviceIndex
selectedDevice = exp.devices[decision.targetDeviceIndex]
third.decision = decision	
third.setprocessingNode(selectedDevice)
dev2.addJob(third)
exp.simulateTime(sim.constants.PLOT_TD * 10)
print ("offload 1 0")
time.sleep(1)
# batch 2 

# offload from 0 to 0
fourth = sim.job.job(exp.time, dev, 5, dev.decision, hardwareAccelerated=True)
sim.systemState.current.updateDevice(dev)
decision = sim.offloadingDecision.possibleActions[0]
print ('decision', decision)
if decision.local: decision.targetDeviceIndex = sim.systemState.current.selfDeviceIndex
selectedDevice = exp.devices[decision.targetDeviceIndex]
fourth.decision = decision
fourth.setprocessingNode(selectedDevice)
dev.addJob(fourth)
# batch 3 
print ("offload 0 0")
exp.simulateUntilJobDone()
exp.simulateUntilJobDone()
exp.simulateUntilJobDone()
time.sleep(1)

print("job done")
exp.simulateTime(sim.constants.PLOT_TD * 100)

	