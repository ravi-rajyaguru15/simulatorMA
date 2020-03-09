import multiprocessing

import sim
from sim import debug
from sim.devices.components import powerPolicy
from sim.experiments.experiment import setupMultithreading
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.offloading import offloadingPolicy
from sim.simulations import constants, variable, localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation

if __name__ == "__main__":
	setupMultithreading()
	localConstants.DEBUG_HISTORY = False
	# debug.settings.learnEnabled = True
	debug.settings.infoEnabled = True

	# debug.settings.enabled = True
	# debug.settings.learnEnabled = True
	exp = SimpleSimulation(numDevices=2, maxJobs=1, agentClass=lazyAgent)
	exp.scenario.setInterval(1)
	exp.setBatterySize(1e-2)
	exp.setFpgaIdleSleep(1e-3)
	exp.simulateEpisode()

	debug.settings.infoEnabled = False
	exp.sharedAgent.printModel()

	for i in range(10):
		for j in range(int(1e3)):
			exp.simulateEpisode()
		exp.sharedAgent.printModel()

	exp.sharedAgent.printModel()
