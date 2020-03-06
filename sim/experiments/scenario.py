import traceback

import numpy as np

from sim import debug
from sim.clock import clock
from sim.devices.node import node
from sim.simulations import constants
# from sim.simulations.SimpleSimulation import NEW_JOB
# from sim.simulations.variable import Constant


class scenario:
	name = None
	devicePolicy = None
	devices = None
	defaultDevices = None
	previousDevice = None

	def __init__(self, devicePolicyClass, devices=None):
		# self.name = name
		self.tasks = []
		self.devicePolicy = devicePolicyClass
		self.devices = devices

	def __repr__(self):
		return "<%s Scenario: %s>" % (self.name, self.devicePolicy.name)

	def setDevices(self, devices):
		# print("set devices to", devices)
		self.devices = list(devices)
		self.defaultDevices = devices

		# queue initial jobs
		return self.queueInitialJobs()

	def removeDevice(self, device):
		# print("removing", device, "from", self.devices)
		if device in self.devices:
			self.devices.remove(device)

	def nextTime(self, currentTime):
		raise Exception("Not implemented")

	def queueInitialJobs(self):
		self.devices = list(self.defaultDevices)
		return self.addJob(self.nextTime(0), self.devices)
	# def getTasks(self):
	# 	return self.tasks

	@staticmethod
	def _addTask(time, taskType, devices=None, subtask=None):
		tasks = []
		for device in devices:
			tasks.append((time, taskType, device, subtask))
		return tasks

		# choose device based on policy
		# if self.devicePolicy == ALL_DEVICES:
		# 	for device in self.devices:
		# 		self.tasks.append((time, taskType, device, subtask))
		# elif self.devicePolicy == RANDOM_DEVICE:
		# 	self.tasks.append((time, taskType, np.choose(self.devices)))
		# else:
		# 	print

	def addJob(self, time, devices):
		chosenDevices = self.devicePolicy.chooseDevice(devices)
		debug.out("add job: %f %s" % (time, chosenDevices))
		# traceback.print_stack()
		# return scenario._addTask(time, NEW_JOB, chosenDevices)
		return [(time, device) for device in chosenDevices]

	def nextJob(self, device=None, time=None):
		if device is None:
			device = self.previousDevice
		nextDevice = self.devicePolicy.nextDevice(device, self.devices)
		nextTime = self.nextTime(time)
		self.previousDevice = nextDevice
		debug.out("next job: %f %s" % (nextTime, nextDevice))
		return nextTime, nextDevice

	def reassignJob(self, device):
		return self.devicePolicy.nextDevice(device, self.devices)



class devicePolicy:
	name = None

	def __init__(self, name):
		self.name = name

	def __repr__(self): return self.name # self.__class__.name

	@staticmethod
	def nextDevice(currentDevice, devices):
		raise Exception("Not implemented")


def convertCurrentTime(currentTime):
	if isinstance(currentTime, clock):
		return currentTime.current
	elif isinstance(currentTime, node):
		return currentTime.currentTime.current
	elif currentTime is None:
		return 0
	else:
		return currentTime


class allDevices(devicePolicy):
	name = "All Devices"

	@staticmethod
	def chooseDevice(devices):
		return devices

	@staticmethod
	def nextDevice(currentDevice, devices):
		if currentDevice is None:
			return devices[0]
		else:
			return currentDevice


class randomDevice(devicePolicy):
	name = "Random Devices"

	@staticmethod
	def chooseDevice(devices):
		return [np.random.choice(devices)]

	@staticmethod
	def nextDevice(currentDevice, devices):
		return randomDevice.chooseDevice(devices)[0]


class roundRobin(devicePolicy):
	name = "Round Robin"
	index = 0

	@staticmethod
	def chooseDevice(devices):
		device = devices[roundRobin.index]
		if roundRobin.index >= len(devices) - 1:
			roundRobin.index = 0
		else:
			roundRobin.index += 1
		return [device]

	@staticmethod
	def nextDevice(currentDevice, devices):
		if currentDevice is None:
			return devices[0]
		else:
			nextIndex = currentDevice.index + 1
			if nextIndex >= len(devices):
				nextIndex = 0
			return devices[nextIndex]


class regularScenario(scenario):
	timeInterval = None
	totalTime = None
	name = "Regular"

	def __init__(self, devicePolicyClass, timeInterval=constants.DEFAULT_TIME_INTERVAL):
		super().__init__(devicePolicyClass=devicePolicyClass)
		self.timeInterval = timeInterval
	# 	self.totalTime = totalTime

	def getTasks(self, totalTime, devices):
		# create regular tasks until time runs out
		tasks = []
		for time in np.linspace(0, stop=totalTime, num=round(totalTime/self.timeInterval)+1):
			for task in self.addJob(time, devices):
				tasks.append(task)
		return tasks

	def nextTime(self, currentTime):
		return convertCurrentTime(currentTime) + self.timeInterval


class randomScenario(scenario):
	timeIntervalVariable = None

	totalTime = None
	name = "Random"

	def __init__(self, devicePolicyClass, timeInterval=constants.JOB_INTERVAL):
		super().__init__(devicePolicyClass=devicePolicyClass)
		self.timeIntervalVariable = timeInterval

	def nextTime(self, currentTime):
		return convertCurrentTime(currentTime) + self.timeIntervalVariable.gen()


REGULAR_SCENARIO_RANDOM = regularScenario(devicePolicyClass=randomDevice)
REGULAR_SCENARIO_ALL = regularScenario(devicePolicyClass=allDevices)
REGULAR_SCENARIO_ROUND_ROBIN = regularScenario(devicePolicyClass=roundRobin)

RANDOM_SCENARIO_RANDOM = randomScenario(devicePolicyClass=randomDevice)
RANDOM_SCENARIO_ALL = randomScenario(devicePolicyClass=allDevices)
RANDOM_SCENARIO_ROUND_ROBIN = randomScenario(devicePolicyClass=roundRobin)

ALL_SCENARIOS = [REGULAR_SCENARIO_ALL, REGULAR_SCENARIO_RANDOM, REGULAR_SCENARIO_ROUND_ROBIN, RANDOM_SCENARIO_ALL, RANDOM_SCENARIO_RANDOM, RANDOM_SCENARIO_ROUND_ROBIN]