import sim.experiments.experiment
import sim.constants
import sim.variable
import sim.offloadingPolicy
import sim.powerPolicy
import sim.debug
from sim.simulation import simulation

if __name__ == '__main__':
	sim.debug.enabled = True
	sim.debug.learnEnabled = True

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.FPGA_IDLE_SLEEP = 0.1
	sim.constants.NUM_DEVICES = 1
	sim.constants.DRAW_DEVICES = False
	sim.constants.MINIMUM_BATCH = 1e10
	sim.constants.PLOT_TD = sim.constants.TD * 10
	sim.constants.DEFAULT_ELASTIC_NODE.RECONFIGURATION_TIME = sim.variable.Constant(sim.constants.TD * 2)

	exp = simulation(True)
	sim.simulation.current = exp

	exp.simulateTime(sim.constants.PLOT_TD * 1)
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
	exp.simulateTime(sim.constants.PLOT_TD * 10)

