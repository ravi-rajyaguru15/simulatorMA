from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.qTableAgent import qTableAgent


class minimalTableAgent(minimalAgent, qTableAgent):
	__name__ = "Minimal Table Agent"
	def __repr__(self): return "<%s>" % __name__


