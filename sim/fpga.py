import numpy as np

from sim.result import result
import sim.constants 
from sim.processor import processor
from sim.component import component
import sim.powerState 

class fpga(processor):
	busyColour = (0, 0, 1, 1)
	idleColour = (0, 0, 0.5, 1)
	sleepColour = (0, 0, 0.2, 1)
	reconfigurationColour = (0, 0, 0.25, 1)

	currentConfig = None
	reconfigurationCurrent = [sim.constants.FPGA_RECONFIGURATION_INT_CURRENT, sim.constants.FPGA_RECONFIGURATION_AUX_CURRENT]

	def __init__(self):
		processor.__init__(self, 
			voltage = [sim.constants.FPGA_INT_VOLTAGE, sim.constants.FPGA_AUX_VOLTAGE],
			activeCurrent = [sim.constants.FPGA_ACTIVE_INT_CURRENT, sim.constants.FPGA_ACTIVE_AUX_CURRENT],
			idleCurrent = [sim.constants.FPGA_IDLE_INT_CURRENT, sim.constants.FPGA_IDLE_AUX_CURRENT],
			sleepCurrent = [sim.constants.FPGA_SLEEP_INT_CURRENT, sim.constants.FPGA_SLEEP_AUX_CURRENT],
			processingSpeed = sim.constants.FPGA_PROCESSING_SPEED)

	# power states
	def reconfigure(self, task):
		self.currentConfig = task
		self.busyColour = task.colour
		# print ("changed fpga colour")
		self.state = sim.powerState.RECONFIGURING

	# loses configuration when it sleeps
	def sleep(self):
		self.currentConfig = None

	def current(self):
		if self.state == sim.powerState.RECONFIGURING:
			return self.reconfigurationCurrent
		else:
			return component.current(self)

	def colour(self):
		if self.state == sim.powerState.RECONFIGURING:
			return self.reconfigurationColour
		else:
			return component.colour(self)

	def isConfigured(self, task):
		assert task is not None
		return self.currentConfig == task


	# def reconfigurationEnergy(self, time):
	# 	return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.reconfigurationCurrent])

 