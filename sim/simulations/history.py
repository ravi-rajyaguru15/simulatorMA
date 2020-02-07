import sim.simulations.history

class history:
	data = None
	fields = ["loss", "reward", "q", "action"]

	def __init__(self):
		self.data = dict()
		for field in history.fields:
			self.data[field] = []

	def add(self, field, data):
		assert field in history.fields

		self.data[field].append(data)

	def combine(self, targetHistory):
		assert targetHistory is not None
		assert isinstance(targetHistory, sim.simulations.history.history)
		for field in history.fields:
			self.data[field] += targetHistory.getField(field)

	def getField(self, field):
		return self.data[field]

	def __repr__(self):
		return "history <{}>".format(str(self.data))