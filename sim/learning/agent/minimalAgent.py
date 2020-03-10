from math import log2

from sim import debug
from sim.learning.agent.qTableAgent import qTableAgent


class minimalAgent(qTableAgent):
	__name__ = "Minimal Agent"
	def __repr__(self): return "<Minimal Agent>"

	def reward(self, job, task, device):
		# default reward behaviour
		jobReward = 100. if job.finished else -50 # * device.numJobsDone
		if job.totalEnergyCost != 0 and device in job.devicesEnergyCost:
			# if device not in job.devicesEnergyCost:
			# 	print(job.creator, job.processingNode, job.owner, job.finished, job.devicesEnergyCost)
			energyReward = -job.devicesEnergyCost[device] / device.maxEnergyLevel * 1e2
			# energyReward = -log2(job.totalEnergyCost)
		else:
			energyReward = 0

		deathReward = -1000. if device.gracefulFailure else 0

		# print(self, device.numJobsDone, jobReward + energyReward)
		return jobReward + energyReward + deathReward

