from sim import debug
from sim.learning.state.systemState import systemState

singles = ['taskIdentifier', 'taskSize', 'selfDeviceIndex', 'selfExpectedLife', 'systemExpectedLife',
		   'deadlineRemaining', 'selfBatch', 'selfCurrentConfig']
multiples = ['expectedLife', 'batchLengths', 'allConfig']

class originalSystemState(systemState):


	def __init__(self, simulation, numDevices):
		systemState.__init__(self, simulation=simulation, numDevices=numDevices, singles=singles, multiples=multiples)

	def updateState(self, task, job, device):
		self.updateSystem()
		debug.learnOut("updating systemState with [{}] [{}] [{}]".format(task, job, device), 'c')
		print("update", self.__class__)
		self.updateTask(task)
		self.updateJob(job)
		self.updateDevice(device)

	def updateSystem(self):
		expectedLifetimes = self.devicesLifetimesFunction()
		self.setField('expectedLife', expectedLifetimes)
		self.setField('systemExpectedLife', self.systemExpectedLifeFunction(expectedLifetimes))

	# update the system state based on which task is to be done
	def updateTask(self, task):
		self.currentTask = task

		# self.batchLengths = self.taskBatchLengthsFunction(task)
		# self.taskIdentifier = task.identifier
		# self.taskSize = task.rawSize

		# sim.debug.out("update task {} {} {} {}".format(self.currentTask, self.batchLengths, self.taskIdentifier, self.taskSize))
		self.setField('batchLengths', self.taskBatchLengthsFunction(task))
		self.setField('taskIdentifier', task.identifier)
		self.setField('taskSize', task.rawSize)

	# sim.debug.out(self.dictRepresentation)

	# self.update()

	def updateJob(self, job):
		# self.deadlineRemaining = np.max([0, job.deadlineTime - self.currentTime.current])
		# sim.debug.out('update job {}'.format(self.deadlineRemaining))
		remaining = job.deadlineTime - self.currentTime.current
		self.setField('deadlineRemaining', remaining if remaining >= 0 else 0)

	# sim.debug.out(self.dictRepresentation)
	# self.update()

	def updateDevice(self, device):
		# self.selfBatch = len(device.batch[self.currentTask]) if self.currentTask is not None and self.currentTask in device.batch else 0
		# self.selfExpectedLife = device.expectedLifetime()
		# self.selfDeviceIndex = device.index

		# if device.hasFpga():
		# 	if device.fpga.currentConfig is not None:
		# 		self.selfCurrentConfiguration = device.fpga.currentConfig.identifier
		# 	else:
		# 		self.selfCurrentConfiguration = 0
		# else:
		# 	self.selfCurrentConfiguration = 0

		# print('update device', self.selfBatch, self.selfExpectedLife, self.selfDeviceIndex)
		self.setField('selfBatch', len(
			device.batch[self.currentTask]) if self.currentTask is not None and self.currentTask in device.batch else 0)
		self.setField('selfExpectedLife', device.expectedLifetime())
		self.setField('selfDeviceIndex', device.index)

		self.setField('selfCurrentConfig', device.getCurrentConfiguration())

# sim.debug.out(self.dictRepresentation)

# self.update()
# sys.exit(0)
