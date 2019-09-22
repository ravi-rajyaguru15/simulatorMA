import numpy as np
import sim.constants

# used as shared variable
current = None

class systemState:
	simulation = None
	currentTask = None
	currentState = None
	
	# simulation states
	batchLengths = [None]
	expectedLife = None
	# self states
	selfDeviceIndex = None
	selfBatch = None
	selfExpectedLife = None
	selfCurrentConfiguration = None
	# task states
	taskSize = None
	taskIdentifier = None
	deadlineRemaining = None
	currentTime = None # not added as input 
	# task size, data size, identifier, current config, deadline

	stateCount = None

	def __init__(self): # , simulation):
	# 	self.simulation = simulation
	# 	print("statecount", self.stateCount)
		self.stateCount = sim.constants.NUM_DEVICES * 2 + 7
		self.batchLengths = [0] * sim.constants.NUM_DEVICES

	def __repr__(self):
		return str(self.currentState)

	def updateSystem(self, simulation):
		# self.stateCount = simulation.constants.NUM_DEVICES * 2 + 7
		self.simulation = simulation

		self.expectedLife = simulation.devicesLifetimes()
		self.systemExpectedLife = simulation.systemLifetime()
		self.currentTime = simulation.time

		self.update()

	def update(self):
		elements = [self.taskIdentifier, self.taskSize, self.selfDeviceIndex, self.selfExpectedLife, self.systemExpectedLife, self.expectedLife, self.deadlineRemaining, self.selfBatch, self.batchLengths]
		# ensure everything is a list 
		elements = [element if isinstance(element, list) else [element] for element in elements]
		# flatten into single list
		self.currentState = [lst for element in elements for lst in element]
		
		if len(self.currentState) != self.stateCount:
			print(self.currentState)
			print(elements)

		assert len(self.currentState) == self.stateCount

	def onehot(self, index):
		return np.array([1.0 if i == index else 0.0 for i in range(systemState.stateCount)])

	# update the system state based on which task is to be done
	def updateTask(self, task):
		self.currentTask = task
		
		self.batchLengths = self.simulation.taskBatchLengths(task)
		self.taskIdentifier = task.identifier
		self.taskSize = task.rawSize

		self.update()

	def updateJob(self, job, currentTime):
		self.deadlineRemaining = np.max([0, job.deadlineTime - currentTime])

		self.update()

	def updateDevice(self, device):
		self.selfBatch = len(device.batch[self.currentTask]) if self.currentTask is not None and self.currentTask in device.batch else 0
		self.selfExpectedLife = device.expectedLifetime()
		self.selfDeviceIndex = device.index

		if device.hasFpga():
			if device.fpga.currentConfig is not None:
				self.selfCurrentConfiguration = device.fpga.currentConfig.identifier
			else:
				self.selfCurrentConfiguration = 0
		else:
			self.selfCurrentConfiguration = 0

		self.update()
