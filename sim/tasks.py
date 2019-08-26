class task:
	colour = None
	name = None
	complexity = None

	def __init__(self, name, colour, complexity):
		self.name = name
		self.colour = colour
		self.complexity = complexity

	def __repr__(self):
		return self.name

EASY = task(
	"Easy",
	colour=(1, 1, 0, 1), 
	complexity=8e3
	)

HARD = task(
	"Hard",
	colour=(1, 0, 1, 1), 
	complexity=10e3
	)

