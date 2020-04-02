import multiprocessing

import sim
from sim import debug
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

	np.set_printoptions(suppress=True)
	# debug.settings.enabled = True
	# debug.settings.learnEnabled = True
	for agent in [lazyTableAgent]: # minimalTableAgent
		exp = SimpleSimulation(numDevices=2, maxJobs=2, agentClass=agent)
		exp.scenario.setInterval(1)
		exp.setBatterySize(1e-2)
		print("pretraining...")
		for i in range(int(1)):
			exp.simulateEpisode()
		print("testing")

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
		exp.sharedAgent.printModel()
		#
		# for i in range(10):
		# 	for j in range(int(1e3)):
		# 		exp.simulateEpisode()
		# 	exp.sharedAgent.printModel()
		#
		# exp.sharedAgent.printModel()
