import random

# current usage in mA
WIRELESS_RX_CURRENT = [19., 23.0] #
WIRELESS_TX_CURRENT = [19., 23.0] #

MCU_ACTIVE_CURRENT = [8., 16.4]
MCU_IDLE_CURRENT = [.5, .5] #

FPGA_ACTIVE_INT_CURRENT = [12.2, 14.5]
FPG_IDLE_INT_CURRENT = [0, 0]
FPGA_ACTIVE_AUX_CURRENT = [8.1, 9.]
FPG_IDLE_AUX_CURRENT = [0, 0]

# speeds in kB/s
WIRELESS_SPEED = [250/8., 250/8.] #
ETHERNET_SPEED = [100. * 1024., 1000. * 1024.] #
MCU_PROCESSING_SPEED = [1000./8., 1000./6.4]
FPGA_PROCESSING_SPEED = [320000, 320000] # 32 MHz * 10 neurons
SERVER_PROCESSING_SPEED = [1000./8./16*3000, 1000./6.4/16*3000] # mcu * 3GHz / 16MHz
MCU_FPGA_COMMUNICATION_SPEED = [2000., 2000.] # 4cl * 8MHz

# time in s
MCU_MW_OVERHEAD_LATENCY = [20e-3, 25e-3]
MCU_MESSAGE_OVERHEAD_LATENCY = [1e-3, 4e-3] #
SERVER_MESSAGE_OVERHEAD_LATENCY = [1e-4, 1.1e-4] #
ETHERNET_PING = [5. / 1000., 15. / 1000.] #

# voltage in V
MCU_VOLTAGE = [3.3, 3.3] #
FPGA_INT_VOLTAGE = [1.2, 1.2] #
FPGA_AUX_VOLTAGE = MCU_VOLTAGE

# size in bytes
SAMPLE_RAW_SIZE = [4, 4] # FRAGMENTATION
SAMPLE_PROCESSED_SIZE = [1, 1] #

def randomise(range):
	return random.uniform(range[0], range[1])