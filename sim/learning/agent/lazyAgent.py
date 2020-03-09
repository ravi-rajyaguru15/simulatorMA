from math import log2, log

from sim import debug
from sim.learning.agent.qTableAgent import qTableAgent


class lazyAgent(qTableAgent):
	__name__ = "Lazy Agent"
	def __repr__(self): return "<Lazy Agent>"

	def reward(self, job, task, device):
		debug.learnOut("energy cost %f" % job.totalEnergyCost)
		if job.totalEnergyCost == 0:
			energyReward = 0
		else:
			energyReward = -job.totalEnergyCost / device.maxEnergyLevel * 1e2

		# print(0.1 / device.maxEnergyLevel, 0.2 / device.maxEnergyLevel)

		deathReward = -100 if device.gracefulFailure else 0

		jobReward = energyReward + deathReward # -log2(job.totalEnergyCost * 1e3)
		# print(job.totalEnergyCost, device.maxEnergyLevel, jobReward)
		# print(self, jobReward, )

		return jobReward