import sim.variable

class task:
	colour = None
	name = None
	complexity = None
	rawSize = None
	processedSize = None
	identifier = 0
	deadline = None

	def __init__(self, name, colour, complexity, rawSize, processedSize, deadline):
		self.name = name
		self.colour = colour
		self.complexity = complexity
		self.rawSize = rawSize
		self.processedSize = processedSize
		self.deadline = deadline

		task.identifier += 1
		self.identifier = task.identifier

	def __repr__(self):
		return self.name

# SAMPLE_RAW_SIZE = Constant(400, integer=True) # FRAGMENTATION
# SAMPLE_PROCESSED_SIZE = Constant(100, integer=True) #

EASY = task(
	"Easy",
	colour=(1, 1, 0, 1), 
	complexity=8e3,
	rawSize=5,
	processedSize=1,
	deadline=sim.variable.Gaussian(5, 0.1)
	)

HARD = task(
	"Hard",
	colour=(1, 0, 1, 1), 
	complexity=10e6,
	rawSize=1e3,
	processedSize=10,
	deadline=sim.variable.Gaussian(5, 0.5)
	)

