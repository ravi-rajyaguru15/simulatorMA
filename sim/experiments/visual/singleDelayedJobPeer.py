

# @staticmethod
def singleDelayedJobPeer(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY
	
	exp = simulation()

	sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.DEFAULT_TASK_GRAPH = [sim.tasks.EASY]

	exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=accelerated)
	exp.simulateTime(sim.constants.PLOT_TD * 150)
