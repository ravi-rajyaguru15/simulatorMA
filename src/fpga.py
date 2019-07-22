from result import result
import constants 
from processor import processor

class fpga(processor):

	def __init__(self):
		processor.__init__(self, 
			voltage = [constants.FPGA_INT_VOLTAGE, constants.FPGA_AUX_VOLTAGE],
			activeCurrent = [constants.FPGA_ACTIVE_INT_CURRENT, constants.FPGA_ACTIVE_AUX_CURRENT],
			idleCurrent = [constants.FPG_IDLE_INT_CURRENT, constants.FPG_IDLE_AUX_CURRENT],
			messageOverheadLatency = constants.MCU_MESSAGE_OVERHEAD_LATENCY,
			processingSpeed = constants.FPGA_PROCESSING_SPEED)