import sim.simulations.constants

class clock:
	current = None
	
	def __init__(self):
		self.reset()
	
	def reset(self):
		self.current = 0

	def __add__(self, target):
		return self.current + target

	def __gt__(self,target):
		return self.current > target

	def __lt__(self, target):
		return self.current < target

	def __truediv__(self, target):
		return self.current / target
	
	def __sub__(self, target):
		return self.current - target

	def __repr__(self):
		return "{:.3f}".format(self.current)

	def set(self, value):
		self.current = value

	def increment(self):
		self.current += sim.simulations.constants.TD
