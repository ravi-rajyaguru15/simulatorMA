from sim.learning.agent.dqnAgent import dqnAgent
from sim.learning.agent.minimalAgent import minimalAgent


class minimalDeepAgent(minimalAgent, dqnAgent):
	__name__ = "Minimal Deep Agent"
	def __repr__(self): return "<%s>" % __name__


