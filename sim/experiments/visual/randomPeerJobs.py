
	
# @staticmethod
def randomPeerJobs(accelerated=True):
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY
	sim.constants.DRAW_DEVICES = True
	sim.constants.PLOT_TD = sim.constants.TD

	exp = simulation(0, 4, 0, hardwareAccelerated=accelerated)

	sim.constants.JOB_LIKELIHOOD = 5e-2
	exp.simulateTime(sim.constants.PLOT_TD * 100)
	