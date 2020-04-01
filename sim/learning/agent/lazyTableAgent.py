from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.qTableAgent import qTableAgent


class lazyTableAgent(lazyAgent, qTableAgent):
	__name__ = "Lazy Table Agent"
	def __repr__(self): return "<%s>" % __name__


