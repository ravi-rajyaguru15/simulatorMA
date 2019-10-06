import sim.constants
import sim.offloadingPolicy
import sim.systemState
import sim.offloadingDecision
import sim.experiments.experiment
import sim.job
import sim.counters
import sim.powerPolicy
import sim.debug
from sim.simulation import simulation
import sys

if __name__ == '__main__':
	sim.debug.enabled = True
	sim.debug.learnEnabled = True

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.FPGA_IDLE_SLEEP = 0.1
	sim.constants.NUM_DEVICES = 2
	sim.constants.DRAW_DEVICES = False
	sim.constants.MINIMUM_BATCH = 1e10
	sim.constants.PLOT_TD = sim.constants.TD * 10

	exp = simulation(True)
	sim.simulation.current = exp

	exp.simulateTime(sim.constants.PLOT_TD * 1)
	dev = exp.devices[0]
	dev2 = exp.devices[1]

	# fix decision to local
	print("job: first")
	sim.experiments.experiment.doLocalJob(exp, dev)

	exp.simulateTime(0.1)

	print("job: second")
	sim.experiments.experiment.doWaitJob(exp, dev)

	# offload from 1 to 0 then wait
	print('\n\n\n\n\n')
	sim.experiments.experiment.doOffloadJob(exp, dev2, dev)

	# offload from 0 to 1 to 0 then wait
	print("\n\n\n\n\n")
	print("job: fourth")
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
	sim.debug.enabled = True
	print("**")
	decision = sim.offloadingDecision.possibleActions[2]
	decision.updateDevice(dev)
	fourth.setDecisionTarget(decision)
	# time.sleep(1)
	# batch 3
	assert fourth.immediate == False
	print("\n\nshould activate now...")
	exp.simulateTick()
	exp.simulateTime(0.1)



	# offload from 0 to 0
	print("job: fifth")
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

