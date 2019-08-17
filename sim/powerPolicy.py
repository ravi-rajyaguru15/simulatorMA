class powerPolicy:
    name = None

    def __init__(self, name):
        self.name = name

STAYS_ON = powerPolicy("Stays On")
IMMEDIATELY_OFF = powerPolicy("Immediately Off")
IDLE_TIMEOUT = powerPolicy("Idle Timout")