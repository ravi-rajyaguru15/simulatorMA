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
	reconfigurationPower = None
	# [self.platform.FPGA_RECONFIGURATION_INT_Power, self.platform.FPGA_RECONFIGURATION_AUX_CURRENT]

	def __init__(self, owner):
		self.reconfigurationPower = [owner.platform.FPGA_RECONFIGURATION_INT_POWER, owner.platform.FPGA_RECONFIGURATION_AUX_POWER]
    		
		processor.__init__(self, owner,
			# voltage = [platform.FPGA_ INT_VOLTAGE, platform.FPGA_AUX_VOLTAGE],
			activePower = [owner.platform.FPGA_ACTIVE_INT_POWER, owner.platform.FPGA_ACTIVE_AUX_POWER],
			idlePower = [owner.platform.FPGA_IDLE_INT_POWER, owner.platform.FPGA_IDLE_AUX_POWER],
			sleepPower = [owner.platform.FPGA_SLEEP_INT_POWER, owner.platform.FPGA_SLEEP_AUX_POWER],
			processingSpeed = owner.platform.FPGA_PROCESSING_SPEED, 
			idleTimeout = sim.constants.FPGA_IDLE_SLEEP)

	def timeOutSleep(self):
		# do not sleep until done with batch
		if self.owner.currentBatch is None:
			# check if it's time to sleep device
			if sim.constants.FPGA_POWER_PLAN == sim.powerPolicy.IDLE_TIMEOUT:
				processor.timeOutSleep(self)
			elif sim.constants.FPGA_POWER_PLAN == sim.powerPolicy.IMMEDIATELY_OFF and self.isIdle():
				self.sleep()
			

	# power states
	def reconfigure(self, task):
		self.currentConfig = task
		self.busyColour = task.colour
		# print ("changed fpga colour")
		self.state = sim.powerState.RECONFIGURING

	# loses configuration when it sleeps
	def sleep(self):
		self.currentConfig = None
		processor.sleep(self)

	# def current(self):
	# 	if self.state == sim.powerState.RECONFIGURING:
	# 		return self.reconfigurationCurrent
	# 	else:
	# 		return component.current(self)

	def power(self):
		if self.state == sim.powerState.RECONFIGURING:
			return component._total(self.reconfigurationPower)
		else:
			return component.power(self)

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

 