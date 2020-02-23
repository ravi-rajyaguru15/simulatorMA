from math import log2

from sim import debug
from sim.learning.agent.qTableAgent import qTableAgent


class lazyAgent(qTableAgent):
	def reward(self, job):
		debug.learnOut("energy cost %f" % job.totalEnergyCost)
		jobReward = -log2(job.totalEnergyCost)

		return jobReward