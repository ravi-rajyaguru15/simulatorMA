from sim import debug
from sim.learning.agent.qTableAgent import qTableAgent


class minimalAgent(qTableAgent):
	def reward(self, job):
		# default reward behaviour
		jobReward = 1. if job.finished else -.5

		return jobReward

