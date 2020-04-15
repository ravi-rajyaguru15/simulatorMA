from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.agent.qTableAgent import qTableAgent
from sim.learning.agent.regretfulAgent import regretfulAgent


class regretfulTableAgent(regretfulAgent, qTableAgent):
	__name__ = "Regretful Table Agent"
	def __repr__(self): return "<%s>" % __name__


