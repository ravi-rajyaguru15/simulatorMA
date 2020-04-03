import multiprocessing

import sim
from sim import debug, plotting
from sim.devices.components import powerPolicy
from sim.experiments.experiment import setupMultithreading
import numpy as np
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.offloading import offloadingPolicy
from sim.simulations import constants, variable, localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation

if __name__ == "__main__":
	setupMultithreading()

	np.set_printoptions(suppress=True, precision=2)
	debug.settings.learnEnabled = True # change this to see debug on how it learns

	for agent in [lazyTableAgent]: # minimalTableAgent
		exp = SimpleSimulation(numDevices=2, maxJobs=2, agentClass=agent)
		exp.scenario.setInterval(1)
		exp.setBatterySize(1e-2)
		print("pretraining...")
		for i in range(int(1)): # change this to train longer (i'm using 1e3 to get a decent view)
			debug.learnOut('\n')
			exp.simulateEpisode()
			debug.learnOut('\n')

		# print("testing")

		localConstants.DEBUG_HISTORY = False
		# debug.settings.learnEnabled = True
		# debug.settings.enabled = True
		# debug.settings.infoEnabled = True

		# exp.setFpgaIdleSleep(1e-3)
		exp.simulateEpisode()

		# print(exp.sharedAgent.__name__)
		# print([device.totalSleepTime / device.currentTime.current for device in exp.devices])
		# print([device.totalSleepTime for device in exp.devices])
		# print([device.currentTime.current for device in exp.devices])
		# print(exp.numFinishedJobs)

		# debug.settings.infoEnabled = False
		# exp.sharedAgent.printModel()
		plotting.plotModel(exp.sharedAgent)
		#
		# for i in range(10):
		# 	for j in range(int(1e3)):
		# 		exp.simulateEpisode()
		# 	exp.sharedAgent.printModel()
		#
		# exp.sharedAgent.printModel()
