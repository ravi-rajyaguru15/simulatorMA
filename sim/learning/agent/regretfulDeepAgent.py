from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.dqnAgent import dqnAgent
from sim.learning.agent.regretfulAgent import regretfulAgent


class regretfulDeepAgent(regretfulAgent, dqnAgent):
	__name__ = "Regretful Deep Agent"
	def __repr__(self): return "<%s>" % __name__


