import sim.debug as debug
import sim.constants as constants
import sim.simulations as simulations
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation
from sim.offloadingPolicy import *

if __name__ == '__main__':
	print("testing simple simulation")
	constants.NUM_DEVICES = 1
	constants.OFFLOADING_POLICY = LOCAL_ONLY
	debug.enabled = False
	constants.DRAW_DEVICES = False
	simulations.current = Simulation()

	print("\nstarting simulation")
	simulations.current.simulateTick()