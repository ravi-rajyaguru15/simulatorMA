
def singleDelayedJobLocal(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
	sim.constants.MINIMUM_BATCH = 1
	
	exp = simulation(0, 2, 0)

	sim.constants.JOB_LIKELIHOOD = 0
	# exp.en[0].createNewJob()
	# exp.simulateTime(sim.constants.SIM_TIME)
	exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
	exp.simulateTime(0.25)