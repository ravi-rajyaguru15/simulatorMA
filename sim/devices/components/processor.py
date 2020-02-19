import sim.simulations.constants
from sim.devices.components.component import component


class processor(component):
	processingSpeed = None
	idleTime = None
	idleTimeout = None

	rectangle = None

	def __init__(self, owner, activePower, idlePower, sleepPower, processingSpeed, idleTimeout):
		component.__init__(
			self,
			owner,
			# voltage = voltage,
			activePower = activePower,
			idlePower = idlePower,
			sleepPower = sleepPower)

		self.processingSpeed = processingSpeed
		self.idleTime = 0
		self.idleTimeout = idleTimeout

	def processingTime(self, samples, task):
		assert(task is not None)
		# print("processing", samples, self.processingSpeed.gen(), task.complexity, samples / self.processingSpeed.gen() * task.complexity, )
		return samples / self.processingSpeed.gen() * task.complexity


		# if self.idleTime != 0:
		# 	sim.debug.out("idleTime: {:.3f}".format(self.idleTime))
