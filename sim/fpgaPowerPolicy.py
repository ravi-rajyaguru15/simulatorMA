class fpgaPowerPolicy:
    name = None

    def __init__(self, name):
        self.name = name

FPGA_STAYS_ON = fpgaPowerPolicy("FPGA Stays On")
FPGA_IMMEDIATELY_OFF = fpgaPowerPolicy("FPGA Immediately Off")
FPGA_WAIT_OFF = fpgaPowerPolicy("FPGA Wait Off")