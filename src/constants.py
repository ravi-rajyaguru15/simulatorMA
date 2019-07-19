
from variable import *

# current usage in mA
WIRELESS_RX_CURRENT = Gaussian(20., 1.) #
WIRELESS_TX_CURRENT = Gaussian(20., 1.) #

MCU_ACTIVE_CURRENT = Gaussian(12, 2)
MCU_IDLE_CURRENT = Gaussian(.5, 0.1) #

FPGA_ACTIVE_INT_CURRENT = Gaussian(13.5, 1.)
FPG_IDLE_INT_CURRENT = Constant(0)
FPGA_ACTIVE_AUX_CURRENT = Gaussian(8.5, .5)
FPG_IDLE_AUX_CURRENT = Constant(0)

# speeds in kB/s
WIRELESS_SPEED = Constant(250/8.) #
ETHERNET_SPEED = Gaussian(500. * 1024., 50.) #
MCU_PROCESSING_SPEED = Gaussian(1000./8., 10.)
FPGA_PROCESSING_SPEED = Constant(320000) # 32 MHz * 10 neurons
SERVER_PROCESSING_SPEED = Constant(1000./8./16*3000) # mcu * 3GHz / 16MHz
MCU_FPGA_COMMUNICATION_SPEED = Constant(2000.) # 4cl * 8MHz

# time in s
MCU_MW_OVERHEAD_LATENCY = Gaussian(20e-3, 25e-3)
MCU_MESSAGE_OVERHEAD_LATENCY = Gaussian(1e-3, 4e-3) #
SERVER_MESSAGE_OVERHEAD_LATENCY = Gaussian(1e-4, 1.1e-4) #
ETHERNET_PING = Gaussian(5. / 1000., 15. / 1000.) #

# voltage in V
MCU_VOLTAGE = Gaussian(3.3, 3.3) #
FPGA_INT_VOLTAGE = Gaussian(1.2, 1.2) #
FPGA_AUX_VOLTAGE = MCU_VOLTAGE

# size in bytes
SAMPLE_RAW_SIZE = Gaussian(4, 4) # FRAGMENTATION
SAMPLE_PROCESSED_SIZE = Gaussian(1, 1) #

# def randomise(range):
# 	return random.uniform(range[0], range[1])

