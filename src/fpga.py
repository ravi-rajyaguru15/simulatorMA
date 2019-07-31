import numpy as np

from result import result
import constants 
from processor import processor
from component import component
from powerState import powerStates

class fpga(processor):
	busyColour = (0, 0, 1, 1)
	idleColour = (0, 0, 0.5, 1)

	currentConfig = None
	reconfigurationCurrent = [constants.FPGA_RECONFIGURATION_INT_CURRENT, constants.FPGA_RECONFIGURATION_AUX_CURRENT]

	def __init__(self):
		processor.__init__(self, 
			voltage = [constants.FPGA_INT_VOLTAGE, constants.FPGA_AUX_VOLTAGE],
			activeCurrent = [constants.FPGA_ACTIVE_INT_CURRENT, constants.FPGA_ACTIVE_AUX_CURRENT],
			idleCurrent = [constants.FPGA_IDLE_INT_CURRENT, constants.FPGA_IDLE_AUX_CURRENT],
			sleepCurrent = [constants.FPGA_SLEEP_INT_CURRENT, constants.FPGA_SLEEP_AUX_CURRENT],
			processingSpeed = constants.FPGA_PROCESSING_SPEED)

	def current(self):
		if self.state == powerStates.RECONFIGURING:
			return self.reconfiguringCurrent
		else:
			return component.current(self)

	def isConfigured(self, task):
		assert task is not None
		return self.currentConfig == task

	def reconfigure(self, task):
		self.currentConfig = task
		self.busyColour = task.colour
		print ("changed fpga colour")

	def reconfigurationEnergy(self, time):
		return time * np.dot([voltage.gen() for voltage in self.voltage], [current.gen() for current in self.reconfigurationCurrent])

 