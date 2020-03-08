from sim import debug
from sim.simulations import constants
from sim.simulations.SimpleSimulation import SimpleSimulation

constants.NUM_DEVICES = 2
constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e-1

debug.settings.enabled = False
debug.settings.learnEnabled = False

exp = SimpleSimulation()
exp.reset()
exp.devices[0].energyLevel = exp.devices[0].gracefulFailureLevel * 1.1 * exp.devices[0].maxEnergyLevel

while not exp.finished:  # and i < 100:
	exp.simulateTick()
