from math import log2, log

from sim import debug
from sim.learning.agent.qAgent import qAgent
from sim.learning.agent.qTableAgent import qTableAgent


class lazyAgent(qAgent):
	__name__ = "Lazy Agent"
	def __repr__(self): return "<Lazy Agent>"

	def reward(self, job, task, device):
		debug.out("energy cost %f" % job.totalEnergyCost)
		jobReward = 100. if job.finished else -50 # * device.numJobsDone

		if job.totalEnergyCost != 0 and device in job.devicesEnergyCost:
			# if device not in job.devicesEnergyCost:
			# 	print(job.creator, job.processingNode, job.owner, job.finished, job.devicesEnergyCost)
			energyReward = -job.devicesEnergyCost[device] / device.maxEnergyLevel * 1e2
		# energyReward = -log2(job.totalEnergyCost)
		else:
			energyReward = 0

		# print(0.1 / device.maxEnergyLevel, 0.2 / device.maxEnergyLevel)

		deathReward = -100 if device.gracefulFailure else 0

		# jobReward = energyReward + deathReward # -log2(job.totalEnergyCost * 1e3)
		# print(job.totalEnergyCost, device.maxEnergyLevel, jobReward)
		# print(self, jobReward, )
		debug.learnOut("Reward: %s (%s) e: %.2f d: %.2f" % (self.__name__, self.possibleActions[job.latestAction], energyReward, deathReward), 'y')

		return energyReward + deathReward