from math import log2

from sim import debug
from sim.learning.agent.qTableAgent import qTableAgent


class deathwishAgent(qTableAgent):
	def __repr__(self): return "<Deathwish Agent>"

	def reward(self, job, task, device):
		# default reward behaviour
		jobReward = 1. * device.numJobsDone if job.finished else -.5
		# if job.totalEnergyCost != 0:
		# 	energyReward = -job.totalEnergyCost / device.maxEnergyLevel * 1e2
		# 	# energyReward = -log2(job.totalEnergyCost)
		# else:
		# 	energyReward = 0
		#
		# deathReward = -100 if device.gracefulFailure else 0

		# print(self, device.numJobsDone, jobReward + energyReward)
		return jobReward

