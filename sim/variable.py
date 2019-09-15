import numpy as np
import math
import random 

import sim.constants

class Variable:
	genFunction = genArgs = integer = None
	mean = std = None

	def __init__(self, function, args, integer=False):
		self.genFunction = function
		self.genArgs = args
		self.integer = integer

	def gen(self):
		if sim.constants.MEASUREMENT_NOISE:
			value = self.genFunction(*self.genArgs)
		else:
			value = self.mean
		value = np.max([0, value])
		if self.integer: value = np.round(value)
		return value

	def evaluate(self, value):
		return self.gen() <= value

	# def genGreaterThan(self, value):
	# 	return self.gen() > value
		
class Uniform(Variable):
	limit = None

	def __init__(self, mean, limit, integer=False):
		self.limit = limit
		self.mean = mean
		Variable.__init__(self, random.uniform, (self.mean - self.limit/2, self.mean + self.limit/2, ), integer=integer)

class Constant(Variable):
	def __init__(self, mean, std=0, integer=False):
		self.mean = mean
		Variable.__init__(self, Constant.genConstant, (self.mean, ), integer=integer)

	@staticmethod
	def genConstant(mean):
		return mean


class Gaussian(Variable):
	def __init__(self, mean, std, integer=False):
		self.mean = mean
		self.std = std

		Variable.__init__(self, np.random.normal, (self.mean, self.std, ), integer=integer)

	# def gen(self):
		# return random.gauss(self.mean, self.std)