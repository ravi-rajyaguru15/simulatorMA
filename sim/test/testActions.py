import sys

import sim.counters
import sim.debug
import sim.tasks.job
from sim.devices.components import powerPolicy
from sim.experiments import experiment
from sim.offloading import offloadingPolicy
from sim.simulations import variable, constants
from sim.simulations.TdSimulation import TdSimulation as simulation

if __name__ == '__main__':
	sim.debug.enabled = False
	sim.debug.learnEnabled = True

	constants.JOB_LIKELIHOOD = 0
	constants.OFFLOADING_POLICY = offloadingPolicy.REINFORCEMENT_LEARNING
	constants.FPGA_POWER_PLAN = powerPolicy.IDLE_TIMEOUT
	constants.FPGA_IDLE_SLEEP = 0.1
	constants.NUM_DEVICES = 2
	constants.DRAW_DEVICES = False
	constants.MINIMUM_BATCH = 1e10
	constants.PLOT_TD = constants.TD * 10
	constants.DEFAULT_ELASTIC_NODE.RECONFIGURATION_TIME = variable.Constant(0.003)

	exp = simulation()
	sim.simulations.current = exp

	exp.simulateTime(constants.PLOT_TD * 1)
	dev = exp.devices[0]
	dev2 = exp.devices[1]

	# fix decision to local
	print("job: first")
	experiment.doLocalJob(exp, dev)

	exp.simulateTime(0.1)

	print("job: second")
	experiment.doWaitJob(exp, dev)

	# offload from 1 to 0 then wait
	print('\n\n\n\n\n')
	print("job: third")
	experiment.doOffloadJob(exp, dev2, dev)

	# offload from 0 to 1 to 0 then wait
	print("\n\n\n\n\n")
	print("job: fourth")
	sim.debug.out("FOURTH", 'g')
	fourth = sim.tasks.job.job(dev, 5, hardwareAccelerated=True)
	decision = offloading.offloadingDecision.possibleActions[1]
	decision.updateDevice(dev)
	print("target index", decision.targetDeviceIndex)
	fourth.setDecisionTarget(decision)
	exp.addJob(dev, fourth)
	print("offload 0 1 0")
	while dev2.currentJob is None:
		exp.simulateTick()
		print('\n\n-\n')
	print("dev2 has job again")
	print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)
	decision = offloading.offloadingDecision.possibleActions[0]
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
	sim.debug.enabled = False
	print("**")
	decision = offloading.offloadingDecision.possibleActions[2]
	decision.updateDevice(dev)
	fourth.setDecisionTarget(decision)
	# time.sleep(1)
	# batch 3
	assert fourth.immediate == False
	print("\n\nshould activate now...")
	exp.simulateTick()

	# offload from 0 to 0
	print("job: fifth")
	fifth = sim.tasks.job.job(dev, 5, hardwareAccelerated=True)
	decision = offloading.offloadingDecision.possibleActions[0]
	decision.updateDevice(dev)
	fifth.setDecisionTarget(decision)
	exp.addJob(dev, fifth)
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
	sixth = sim.tasks.job.job(dev, 5, hardwareAccelerated=True)
	decision = offloading.offloadingDecision.possibleActions[3]
	decision.updateDevice(dev)
	print("override sixth")
	print("target index", decision.targetDeviceIndex)
	print("target device", decision.targetDevice)
	sixth.setDecisionTarget(decision)
	exp.addJob(dev, sixth)
	exp.simulateUntilJobDone()
	print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)
	print("local done")
