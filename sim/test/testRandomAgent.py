from sim import debug
from sim.learning.agent.randomAgent import randomAgent
from sim.simulations.SimpleSimulation import SimpleSimulation

if __name__ == "__main__":
	exp = SimpleSimulation(agentClass=randomAgent)
	exp.setBatterySize(1e-1)
	# debug.settings.learnEnabled = True
	# debug.settings.enabled = True
	exp.simulateEpisode()