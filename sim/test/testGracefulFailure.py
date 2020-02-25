from sim import debug
from sim.simulations import constants
from sim.simulations.SimpleSimulation import SimpleSimulation

constants.NUM_DEVICES = 2
constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e-1

debug.enabled = True
debug.learnEnabled = True

exp = SimpleSimulation()
exp.reset()
exp.devices[0].energyLevel = 0.101 * exp.devices[0].maxEnergyLevel

while not exp.finished:  # and i < 100:
	exp.simulateTick()
