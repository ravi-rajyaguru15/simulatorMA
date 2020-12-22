import multiprocessing

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import sim
from sim import debug, plotting
from sim.devices.components import powerPolicy
from sim.experiments.experiment import setupMultithreading
import numpy as np

from sim.experiments.scenario import REGULAR_SCENARIO_RANDOM, REGULAR_SCENARIO_ROUND_ROBIN
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalDeepAgent import minimalDeepAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.state.extendedSystemState import extendedSystemState
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.offloading import offloadingPolicy
from sim.simulations import constants, variable, localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.tasks.tasks import HARD

if __name__ == "__main__":
	setupMultithreading()

	basic = True
	long = False

	np.set_printoptions(suppress=True, precision=2)
	debug.settings.learnEnabled = not long # change this to see debug on how it learns

	systemStateClass = minimalSystemState if basic else extendedSystemState

	for agent in [minimalDeepAgent]: # lazyTableAgent
		exp = SimpleSimulation(numDevices=4, maxJobs=5, reconsiderBatches=False, tasks=[HARD], agentClass=agent, centralisedLearning=True, systemStateClass=systemStateClass, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, trainClassification=False)
		# exp.sharedAgent.createModel(2, 8)
		exp.sharedAgent.loadModel()
		exp.sharedAgent.setProductionMode()
		exp.scenario.setInterval(1)
		exp.setFpgaIdleSleep(1e-3)
		exp.setBatterySize(1e-1)
		# print("pretraining...")
		# numrepeats = 1e5 if long else 1
		# for i in range(int(numrepeats)): # change this to train longer (i'm using 1e3 to get a decent view)
		# 	debug.learnOut('\n')
		# 	exp.simulateEpisode(i)
		# 	debug.learnOut('\n')

		# print("testing")

		localConstants.DEBUG_HISTORY = False
		# debug.settings.learnEnabled = True
		# debug.settings.enabled = True
		# debug.settings.infoEnabled = True

		# exp.setFpgaIdleSleep(1e-3)
		exp.simulateEpisode(0)

		# print(exp.sharedAgent.__name__)
		# print([device.totalSleepTime / device.currentTime.current for device in exp.devices])
		# print([device.totalSleepTime for device in exp.devices])
		# print([device.currentTime.current for device in exp.devices])
		# print(exp.numFinishedJobs)

		# debug.settings.infoEnabled = False
		# exp.sharedAgent.printModel()
		# plotting.plotModel(exp.sharedAgent, drawLabels=True)
		#
		# for i in range(10):
		# 	for j in range(int(1e3)):
		# 		exp.simulateEpisode()
		# 	exp.sharedAgent.printModel()
		#
		# exp.sharedAgent.printModel()
