import numpy as np
import math
import random 

class Variable:
	genFunction = genArgs = integer = None

	def __init__(self, function, args, integer=True):
		self.genFunction = function
		self.genArgs = args
		self.integer = integer

	def gen(self):
		value = np.max([0, self.genFunction(*self.genArgs)])
		if self.integer: value = np.round(value)
		return value

	def evaluate(self, value):
		return self.gen() <= value

	# def genGreaterThan(self, value):
	# 	return self.gen() > value
		
class Uniform(Variable):
	start = end = None

	def __init__(self, start, end, integer=True):
		self.start = start
		self.end = end
		Variable.__init__(self, random.uniform, (self.start, self.end, ), integer=integer)

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