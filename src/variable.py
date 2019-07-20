import random 

class Variable:
	genFunction = genArgs = None

	def __init__(self, function, args):
		self.genFunction = function
		self.genArgs = args

	def gen(self):
		return self.genFunction(*self.genArgs)

	def genGreaterThan(self, value):
		return self.gen() > value
		
class Uniform(Variable):
	start = end = None

	def __init__(self, start, end):
		self.start = start
		self.end = end
		Variable.__init__(self, random.uniform, (self.start, self.end, ))

	# def gen(self):
	# 	return random.uniform(self.start, self.end)


class Constant(Variable):
	mean = std = None

	def __init__(self, mean, std=0):
		self.mean = mean
		Variable.__init__(self, Constant.genConstant, (self.mean, ))

	@staticmethod
	def genConstant(mean):
		return mean


class Gaussian(Variable):
	mean = std = None

	def __init__(self, mean, std):
		self.mean = mean
		self.std = std

		Variable.__init__(self, random.gauss, (self.mean, self.std, ))

	# def gen(self):
		# return random.gauss(self.mean, self.std)