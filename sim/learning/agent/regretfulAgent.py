from sim import debug
from sim.learning.agent.qAgent import qAgent
import numpy as np

class regretfulAgent(qAgent):
	__name__ = "Regretful Agent"
	def __repr__(self): return "<Regretful Agent>"

	def reward(self, job, task, device):
		# default reward behaviour
		# jobReward = 100. if job.finished else -50 # * device.numJobsDone
		# jobReward = 100. * device.numJobsDone
		jobReward = 100. * job.finished if job.finished > 0 else -50 # * device.numJobsDone

		if job.totalEnergyCost != 0 and device in job.devicesEnergyCost:
			# if device not in job.devicesEnergyCost:
			# 	print(job.creator, job.processingNode, job.owner, job.finished, job.devicesEnergyCost)
			energyReward = -job.devicesEnergyCost[device] / device.maxEnergyLevel * 1e2 * 1e2
			# energyReward = -log2(job.totalEnergyCost)
		else:
			energyReward = 0

		deathReward = -100. - np.sum(device.batchLengths()) if device.gracefulFailure else 0

		debug.learnOut("Reward: %s (%s) j: %.2f e: %.2f d: %.2f" % (self.__name__, self.possibleActions[job.latestAction], jobReward, energyReward, deathReward))

		# print(self, device.numJobsDone, jobReward + energyReward)
		return jobReward + energyReward + deathReward

