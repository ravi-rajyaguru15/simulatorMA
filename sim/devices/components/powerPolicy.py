class powerPolicy:
	name = None

	def __init__(self, name):
		self.name = name

	def __repr__(self): return self.name

STAYS_ON = powerPolicy("Stays On")
IMMEDIATELY_OFF = powerPolicy("Immediately Off")
IDLE_TIMEOUT = powerPolicy("Idle Timeout")

OPTIONS = [STAYS_ON, IMMEDIATELY_OFF, IDLE_TIMEOUT]