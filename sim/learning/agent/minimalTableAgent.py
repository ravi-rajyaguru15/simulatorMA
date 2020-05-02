from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.qTableAgent import qTableAgent


class minimalTableAgent(minimalAgent, qTableAgent):
	__name__ = "Basic Table Agent"
	def __repr__(self): return "<%s>" % __name__


