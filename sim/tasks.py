class task:
	colour = None
	complexity = None

	def __init__(self, colour, complexity):
		self.colour = colour
		self.complexity = complexity

EASY = task(
	colour=(1, 1, 0, 1), 
	complexity=8e3
	)

HARD = task(
	colour=(1, 0, 1, 1), 
	complexity=10.
	)
