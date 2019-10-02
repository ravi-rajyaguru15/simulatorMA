
def singleBatchRemote(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY
	
	exp = simulation(0, 2, 0)

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.MINIMUM_BATCH = 2
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(10)
	sim.constants.PLOT_TD = sim.constants.TD * 1
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(400, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(100, integer=True)
	sim.constants.RECONFIGURATION_TIME = sim.variable.Constant(0.05)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF
	# exp.en[0].createNewJob()
	# exp.simulateTime(sim.constants.SIM_TIME)
	exp.simulateTime(0.015)
	# time.sleep(0.5)
	for i in range(sim.constants.MINIMUM_BATCH):
		exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
		exp.simulateTime(0.025)
		# time.sleep(0.5)

	exp.simulateUntilTime(0.5)
		