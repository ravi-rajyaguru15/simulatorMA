class powerStates:
	counter = 0

	value = None
	name = None

	def __init__(self, name):
		self.value = powerStates.counter
		powerStates.counter += 1
		self.name = name
	
	def __repr__(self): return self.name
# power states
IDLE = powerStates("IDLE")
ACTIVE = powerStates("ACTIVE")
RECONFIGURING = powerStates("RECONFIGURING") # special state for FPGA
SLEEP = powerStates("SLEEP")

