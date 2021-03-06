from sim import debug
from sim.learning.agent.qAgent import qAgent


class minimalAgent(qAgent):
	__name__ = "Basic Agent"
	def __repr__(self): return "<Basic Agent>"

	def reward(self, job, task, device):
		# default reward behaviour
		# jobReward = 100. if job.finished else -50 # * device.numJobsDone
		jobReward = 1. * job.finished #if job.finished > 0 else -.5 # * device.numJobsDone
		# jobReward = 1. * device.numJobsDone * 100.
		if job.totalEnergyCost != 0 and device in job.devicesEnergyCost:
			# if device not in job.devicesEnergyCost:
			# 	print(job.creator, job.processingNode, job.owner, job.finished, job.devicesEnergyCost)
			energyReward = -job.devicesEnergyCost[device] / device.maxEnergyLevel * 1e2
			# energyReward = -log2(job.totalEnergyCost)
		else:
			energyReward = 0

		deathReward = -10. if device.gracefulFailure else 0

		latestAction = "None" if job.latestAction is None else self.possibleActions[job.latestAction]
		debug.learnOut(debug.formatLearn("Reward: %s (%s) j: %.2f e: %.2f d: %.2f", (self.__name__, latestAction, jobReward, energyReward, deathReward)))

		reward = jobReward + energyReward + deathReward
		# print("Reward: %20s (% 8s) r: %.2f j: %.2f e: %.2f d: %.2f" % (self.__name__, self.possibleActions[job.latestAction], reward, jobReward, energyReward, deathReward))
		return reward

