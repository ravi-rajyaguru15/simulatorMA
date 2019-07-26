from result import result
import constants 
from processor import processor

class fpga(processor):

	def __init__(self):
		processor.__init__(self, 
			voltage = [constants.FPGA_INT_VOLTAGE, constants.FPGA_AUX_VOLTAGE],
			activeCurrent = [constants.FPGA_ACTIVE_INT_CURRENT, constants.FPGA_ACTIVE_AUX_CURRENT],
			idleCurrent = [constants.FPGA_IDLE_INT_CURRENT, constants.FPGA_IDLE_AUX_CURRENT],
			sleepCurrent = [constants.FPGA_SLEEP_INT_CURRENT, constants.FPGA_SLEEP_AUX_CURRENT],
			processingSpeed = constants.FPGA_PROCESSING_SPEED)