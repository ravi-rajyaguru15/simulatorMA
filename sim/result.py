class result:
	# latency, energy = None, None
	job = None

	def __init__(self, job):
		self.job = job
		self.batchSize = job.batchSize	
		# this.latency = job.latency
		# this.energy = job.energy

	# def __str__(self):
	# 	return str((this.latency, this.energy))

	# def __add__(self, additional):
	# 	return result(latency=this.latency + additional.latency, energy=this.energy + additional.energy)