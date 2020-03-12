from sim.learning.agent.dqnAgent import dqnAgent
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.minimalAgent import minimalAgent


class lazyDeepAgent(lazyAgent, dqnAgent):
	__name__ = "Lazy Deep Agent"
	def __repr__(self): return "<%s>" % __name__


