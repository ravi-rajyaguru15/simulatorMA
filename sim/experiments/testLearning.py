from sim.simulation import simulation

import sim.debug
import sim.devices.components.powerPolicy
import sim.experiments.experiment
import sim.offloading.offloadingPolicy
import sim.simulations.constants

if __name__ == '__main__':
	sim.debug.enabled = True
	sim.debug.learnEnabled = True

	sim.simulations.constants.JOB_LIKELIHOOD = 0
	sim.simulations.constants.OFFLOADING_POLICY = sim.offloading.offloadingPolicy.REINFORCEMENT_LEARNING
	sim.simulations.constants.FPGA_POWER_PLAN = sim.devices.components.powerPolicy.IDLE_TIMEOUT
	sim.simulations.constants.FPGA_IDLE_SLEEP = 0.1
	sim.simulations.constants.NUM_DEVICES = 1
	sim.simulations.constants.DRAW_DEVICES = False
	sim.simulations.constants.MINIMUM_BATCH = 1e10
	sim.simulations.constants.PLOT_TD = sim.simulations.constants.TD * 10
	sim.simulations.constants.DEFAULT_ELASTIC_NODE.RECONFIGURATION_TIME = sim.simulation.variable.Constant(
		sim.simulations.constants.TD * 2)

	exp = simulation(True)
	sim.simulations.current = exp

	exp.simulateTime(sim.simulations.constants.PLOT_TD * 1)
	dev = exp.devices[0]
	# time.sleep(1)

	# fix decision to local
	# adding some batched jobs
	for _ in range(5):
		sim.experiments.experiment.doWaitJob(exp, dev)
		exp.simulateTime(0.1)

	# exp.simulateUntilJobDone()
	# exp.simulateUntilJobDone()
	# exp.simulateUntilJobDone()
	# time.sleep(1)

	print("job done")
	exp.simulateTime(sim.simulations.constants.PLOT_TD * 10)

