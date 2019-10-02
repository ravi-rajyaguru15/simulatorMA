
def deadlock():
	
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(40, integer=True) # TODO: change back to 4
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF

	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY
	sim.constants.JOB_LIKELIHOOD = 0.01
	sim.constants.DEFAULT_TASK_GRAPH = [sim.tasks.EASY]

	sim.constants.MINIMUM_BATCH = 2
	sim.constants.PLOT_TD = sim.constants.TD * 10
	sim.constants.DISPLAY = False

	exp = simulation(0, 4, 0, hardwareAccelerated=False)

	# exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.simulateTime(1)
	# exp.simulateTime(sim.constants.TD)
	# exp.devices[0].createNewJob(exp.time, hardwareAccelerated=False)
	# exp.simulateTime(sim.constants.PLOT_TD * 150)
