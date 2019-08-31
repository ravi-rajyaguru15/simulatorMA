from sim.variable import *
import sim.platforms.platform


# class elasticNodev4(sim.platforms.platform.platform):
# current usage in mA
WIRELESS_RX_CURRENT = Gaussian(20., 1.)
WIRELESS_TX_CURRENT = Gaussian(20., 1.)
WIRELESS_IDLE_POWER = Gaussian(.06853458300026646, 0.00013352351783459598) #
WIRELESS_SLEEP_POWER = Constant(0)

MCU_ACTIVE_POWER = Gaussian(0.04650097560975609, 1.3934494494717667e-05) # 
MCU_IDLE_POWER = Gaussian(0.11246443112176921, 0.006278224220533599) #
MCU_SLEEP_POWER = Gaussian(0.25, 0.1)

FPGA_ACTIVE_INT_POWER = Gaussian(13.5, 1.)
FPGA_ACTIVE_AUX_POWER = Gaussian(8.5, .5)
FPGA_ACTIVE_SRAM_POWER = Constant(0)
FPGA_ACTIVE_IO_POWER = Constant(0)
FPGA_IDLE_INT_POWER = Gaussian(0.010402710027100269, 2.312274147176325e-05) #
FPGA_IDLE_AUX_POWER = Gaussian(0.012105149051490516, 2.8523598472704047e-05) #
FPGA_IDLE_SRAM_POWER = Gaussian(0.004102981029810298, 1.700636475852264e-05) #
FPGA_IDLE_IO_POWER = Gaussian(0.06680813008130079, 3.9495797728427525e-05) #
FPGA_SLEEP_INT_POWER = Constant(0) #
FPGA_SLEEP_AUX_POWER = Constant(0) #
FPGA_SLEEP_SRAM_POWER = Constant(0) #
FPGA_SLEEP_IO_POWER = Constant(0) #
FPGA_RECONFIGURATION_INT_POWER = Gaussian(10., 1.)
FPGA_RECONFIGURATION_AUX_POWER = Gaussian(100., 5.)
FPGA_RECONFIGURATION_SRAM_POWER = Constant(0)
FPGA_RECONFIGURATION_IO_POWER = Constant(0)

# speeds in kB/s
WIRELESS_SPEED = Constant(250/8.)
ETHERNET_SPEED = Gaussian(500. * 1024., 50.)
MCU_F = 8e6
MCU_PROCESSING_SPEED = Constant(MCU_F)
FPGA_F = 32e6
FPGA_PROCESSING_SPEED = Constant(FPGA_F/10*1e5) # 32 MHz * 10 neurons
SERVER_PROCESSING_SPEED = Constant(1000./8./16*3000) # mcu * 3GHz / 16MHz
MCU_FPGA_COMMUNICATION_SPEED = Constant(MCU_F/4) # 4cl * 8MHz -> b/s

# time in s
MCU_BATCHING_LATENCY = Constant(1.0 / MCU_F * 100)
MCU_MW_OVERHEAD_LATENCY = Gaussian(1e-3, 1e-4)
MCU_MESSAGE_OVERHEAD_LATENCY = Gaussian(5e-3, 1e-3)
SERVER_MESSAGE_OVERHEAD_LATENCY = Gaussian(1e-4, 1.1e-4)
ETHERNET_PING = Gaussian(5. / 1000., 15. / 1000.)
RECONFIGURATION_TIME = Constant(0.096) #

# voltage in V
MCU_VOLTAGE = Constant(3.3) #
FPGA_INT_VOLTAGE = Constant(1.2)
FPGA_AUX_VOLTAGE = MCU_VOLTAGE
WIRELESS_VOLTAGE = Constant(3.3)