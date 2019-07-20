from warnings import warn

import constants 
from subtask import *
from result import result
# from node import node

class task:
	size = None
	samples = None
	startTime = None
	host = None
	destination = None

	subtasks = None
	subtaskIndex = None
	currentSubTask = None

	finished = None

	def __init__(self, origin, size=None, samples=None):
		self.host = origin

		if samples is None:
			if size is None:
				warn("Must supply size or samples to create message")
			self.size = size
			self.samples = None
		else:
			self.size = samples * constants.SAMPLE_RAW_SIZE.gen()
			self.samples = samples
		
		self.finished = False


	def setDestination(self, decision):
		self.destination = decision

		# populate subtasks based on types of devices
		if self.host is self.destination:
			print 'local processing'
			# local processing
			self.subtasks = [(processing(self.host, self.host.mcu, self.samples))]
			self.subtaskIndex = 0
		else:
			print 'UNIMPLEMENTED'

	def process(self):
		# figure out which subtask is active
		if self.currentSubTask is None:
			# more subtasks available?
			if self.subtaskIndex >= len(self.subtasks):
				self.finished = True
				return True
			else:
				self.currentSubTask = self.subtasks[self.subtaskIndex]

		# progress subtask 
		self.currentSubTask.tick()

		if self.currentSubTask.finished:
			self.subtaskIndex += 1
			self.currentSubTask = None

	def computeResult(self):
		output = result()

		for sub in self.subtasks:
			output += result(latency=sub.totalDuration, energy=sub.energyCost)

		return output

	# # change message from raw to processed
	# def process(self):
	# 	# if self.samples is None:
	# 	# 	warn("Cannot process message without sample count")
	# 	# self.size = self.samples * constants.SAMPLE_PROCESSED_SIZE.gen()
