import numpy as np

MEASUREMENT_NOISE = True
CACHE_SIZE = int(1e5)
class Variable:
	genFunction = integer = None
	mean = std = None
	cache = []

	def __init__(self, function, integer=False):
		self.genFunction = function
		self.integer = integer

	def gen(self):
		if not MEASUREMENT_NOISE:
			if self.integer:
				return np.round(self.mean)
			else:
				return self.mean
		else:
			value = self.sample()
			# value = self.genFunction(*self.genArgs)
			# value = np.max([0, value])
			# if self.integer: value = np.round(value)
			return value

	def clearCache(self):
		self.cache = []

	def sample(self):
		if len(self.cache) == 0:
			# generate a new set of samples
			arr = self.genFunction(*self.args(), CACHE_SIZE)
			arr[np.where(arr < 0)] = 0
			if self.integer:
				arr = np.round(arr)
			self.cache = arr.tolist()
		
		return self.cache.pop()

	def args(self):
		raise Exception("Defaults args not available")

	def evaluate(self, value):
		return self.gen() <= value

	# def genGreaterThan(self, value):
	# 	return self.gen() > value
		
class Uniform(Variable):
	limit = None

	def __init__(self, mean, limit, integer=False):
		self.limit = limit
		self.mean = mean
		Variable.__init__(self, np.random.uniform, integer=integer)

	def args(self):
		return (self.mean - self.limit / 2, self.mean + self.limit / 2,)

class Constant(Variable):
	def __init__(self, mean, std=0, integer=False):
		self.mean = mean
		Variable.__init__(self, Constant.genConstant, integer=integer)

	@staticmethod
	def genConstant(mean, numSamples=CACHE_SIZE):
		return np.array([mean] * numSamples)

	def args(self):
		return (self.mean, )

class Gaussian(Variable):
	def __init__(self, mean, std, integer=False):
		self.mean = mean
		self.std = std

		Variable.__init__(self, np.random.normal, integer=integer)

	def setMean(self, mean):
		self.mean = mean
		self.genArgs = [self.mean, self.std]
		self.clearCache()

	def args(self):
		return (self.mean, self.std, )

	# def gen(self):
		# return random.gauss(self.mean, self.std)