import sim.simulations.constants
from sim import debug
from sim.simulations import constants


class clock:
	current = None
	owner = None
	
	def __init__(self, owner=None):
		self.reset()
		self.owner = owner
	
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
		return "{:.5f}".format(self.current)

	def set(self, value):
		debug.out("updated clock of %s to %.6f" % (self.owner, value), 'dg')
		self.current = value

	def increment(self, increment=constants.TD):
		debug.out("updated clock of %s by %.6f" % (self.owner, increment), 'dg')
		self.current += increment
