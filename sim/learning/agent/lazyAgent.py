from math import log2, log

from sim import debug
from sim.learning.agent.qTableAgent import qTableAgent


class lazyAgent(qTableAgent):
	def __repr__(self): return "<Lazy Agent>"

	def reward(self, job, task=None, device=None):
		debug.learnOut("energy cost %f" % job.totalEnergyCost)
		jobReward = -log2(job.totalEnergyCost * 1e3)
		# print(self, jobReward, )

		return jobReward