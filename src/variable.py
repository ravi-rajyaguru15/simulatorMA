import random 

class Constant:
	mean = std = None

	def __init__(self, mean, std):
		return __init__(self, mean, 0) # ignore deviation

	def __init__(self, mean):
		self.mean = mean

	def gen(self):
		return self.mean


class Gaussian:
	mean = std = None

	def __init__(self, mean, std):
		self.mean = mean
		self.std = std

	def gen(self):
		return random.gauss(self.mean, self.std)