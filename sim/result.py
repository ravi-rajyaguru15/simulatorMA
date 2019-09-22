class result:
	latency, energy = None, None

	def __init__(this, latency=0., energy=0.):
		this.latency = latency
		this.energy = energy

	def __str__(this):
		return str((this.latency, this.energy))

	def __add__(this, additional):
		return result(latency=this.latency + additional.latency, energy=this.energy + additional.energy)