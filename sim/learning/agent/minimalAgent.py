from math import log2

from sim import debug
from sim.learning.agent.qTableAgent import qTableAgent


class minimalAgent(qTableAgent):
	# __name__ = "Minimal Agent"
	def __repr__(self): return "<Minimal Agent>"

	def reward(self, job):
		# default reward behaviour
		jobReward = 1. if job.finished else -.5
		energyReward = -log2(job.totalEnergyCost)

		return jobReward + energyReward

