
def differentBatchesLocal(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
	
	exp = simulation(0, 2, 0)

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.MINIMUM_BATCH = 2
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(1)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.MCU_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
	sim.constants.PLOT_TD = sim.constants.TD
	sim.constants.RECONFIGURATION_TIME = sim.variable.Constant(0.05)
	exp.simulateTime(0.015)
	for i in range(sim.constants.MINIMUM_BATCH):
		exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated, taskGraph=[sim.tasks.EASY])
		exp.simulateTime(0.015)
		time.sleep(.5)
	# wait until the end	
	if accelerated:
		exp.simulateUntilTime(0.2)
	else:
		exp.simulateUntilTime(0.1)
	for i in range(sim.constants.MINIMUM_BATCH):
		exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated, taskGraph=[sim.tasks.HARD])
		exp.simulateTime(0.015)
		time.sleep(.5)
	# wait until the end
	exp.simulate()

