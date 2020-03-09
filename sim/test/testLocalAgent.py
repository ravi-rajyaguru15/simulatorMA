from sim.learning.agent.localAgent import localAgent
from sim.simulations.SimpleSimulation import SimpleSimulation

if __name__ == "__main__":
	exp = SimpleSimulation(agentClass=localAgent)
	exp.setBatterySize(1e-1)
	# debug.settings.learnEnabled = True
	# debug.settings.enabled = True
	exp.simulateEpisode()