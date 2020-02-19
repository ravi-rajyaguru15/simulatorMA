import random

import numpy as np

import sim.counters
import sim.debug
import sim.offloading.offloadingPolicy
import sim.simulations
from sim.learning.action import action, LOCAL
from sim.offloading.offloadingPolicy import *
from sim.simulations import constants

# devices = None
sharedClock = None


# print(sim.constants.OFFLOADING_POLICY, self.owner, self.options)

class offloadingDecision:
	sharedAgent = None

	options = None
	owner = None
	target = None
	simulation = None
	agent = None
	agentClass = None

	def __init__(self, device, systemState, agentClass):
		self.owner = device
		self.systemState = systemState
		self.agentClass = agentClass

	@staticmethod
	def selectElasticNodes(devices):
		return [node for node in devices if node.hasFpga()]

	@staticmethod
	def createSharedAgent(state, agentClass):
		offloadingDecision.sharedAgent = agentClass(state)
		# print("created shared", offloadingDecision.sharedAgent)
		# sim.learning.offloadingDecision.sharedAgent = agentClass(state)

	def setOptions(self, allDevices):
		# set options for all policies that use it, or select constant target
		# if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.LOCAL_ONLY:
		# 	self.target = self.owner
		if constants.OFFLOADING_POLICY == RANDOM_PEER_ONLY:
			# only offload to something with fpga when needed
			elasticNodes = offloadingDecision.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
			if self.owner in elasticNodes:
				elasticNodes.remove(self.owner)
			self.options = elasticNodes
		elif constants.OFFLOADING_POLICY == SPECIFIC_PEER_ONLY:
			self.target = allDevices[constants.OFFLOADING_PEER]
		elif constants.OFFLOADING_POLICY == ANYTHING \
				or constants.OFFLOADING_POLICY == ANNOUNCED \
				or constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING:
			self.options = offloadingDecision.selectElasticNodes(
				allDevices)  # select elastic nodes from alldevices list]
		# self.target = self.owner
		elif constants.OFFLOADING_POLICY == ROUND_ROBIN:
			# assign static targets (will happen multiple times but that's fine)
			offloadingDecision.options = offloadingDecision.selectElasticNodes(
				allDevices)  # select elastic nodes from alldevices list]
		# elif constants.OFFLOADING_POLICY == LOCAL_ONLY:
		# 	offloadingDecision.options = [self.owner]
		else:
			raise Exception("Unknown offloading policy")

		# setup learning if needed
		if constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING:
			# create either private or shared agent
			if not constants.CENTRALISED_LEARNING:
				self.agent = self.agentClass(self.systemState, allDevices)
			else:
				# create shared agent if required
				assert offloadingDecision.sharedAgent is not None
				self.agent = offloadingDecision.sharedAgent


	def chooseDestination(self, task, job, device):
		# if specified fixed target, return it
		if self.target is not None:
			print("constant target")
			return self.target  # possibleActions[self.target.index]
		# check if shared target exists
		elif offloadingDecision.target is not None:
			print("shared target")
			return offloadingDecision.target  # possibleActions[offloadingDecision.target.index]
		elif self.options is None:
			raise Exception("options are None!")
		elif len(self.options) == 0:
			raise Exception("No options available!")
		else:
			# choose randomly from the options available
			if constants.OFFLOADING_POLICY == ANNOUNCED:
				# every other offloading policy involves randoming
				batches = np.array([len(dev.batch[task]) if task in dev.batch.keys() else 0 for dev in self.options])
				# is the config already available?
				configsAvailable = np.array([dev.fpga.currentConfig == task for dev in self.options])

				decisionFactors = batches + configsAvailable

				# nobody has a batch going
				if np.sum(decisionFactors) == 0:
					# then have to do it yourself
					choice = action.findAction(self.owner.index)
				else:
					raise Exception("arguments incorrect")
					largestBatches = np.argmax(decisionFactors)
					# print('largest:', largestBatches)
					choice = actionFromIndex(self.options[largestBatches].index)
			elif constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING:
				sim.debug.learnOut("deciding how to offload new job")
				sim.debug.learnOut("owner: {}".format(self.owner), 'r')
				choice = self.firstDecideDestination(task, job, device)
			# sim.debug.learnOut("choice: {}".format(choice))
			elif constants.OFFLOADING_POLICY == LOCAL_ONLY:
				choice = LOCAL
				choice.updateTargetDevice(self.owner, [self.owner])
			else:
				choice = action("Random", targetIndex=random.choice(self.options).index)
				choice.updateTargetDevice(self.owner, self.options)
			# choice = np.random.choice(self.options) #  action.findAction(random.choice(self.options).index)

			sim.debug.out("Job assigned: {} -> {}".format(self.owner, choice))
			# if self.privateAgent is not None:
			# 	choice.updateDevice() # self.privateAgent.devices)
			# else:
			# 	choice.updateDevice() # self.options)
			return choice

	# check offloading decision on idle job
	def rechooseDestination(self, task, job, device):
		# self.updateState(task, job, device)
		# self.privateAgent.backward(job.reward(), sim.simulations.current.finished)
		self.train(task, job, device)
		# choice = self.decideDestination(task, job, device)
		choice = self.agent.forward(task, job, device)

		job.setDecisionTarget(choice)
		return job.activate()

		# return choice

	# update decision to see if should be uploaded again
	def redecideDestination(self, task, job, device):
		assert constants.OFFLOADING_POLICY == REINFORCEMENT_LEARNING
		# print("redeciding")
		self.train(task, job, device)
		return self.agent.forward(task, job, device)

	# decide initial decision for job
	def firstDecideDestination(self, task, job, device):
		return self.agent.forward(task, job, device)

	def updateState(self, task, job, device):
		# update state
		self.systemState.updateState(task, job, device)

	def train(self, task, job, device):
		sim.debug.learnOut("Training: [{}] [{}] [{}]".format(task, job, device), 'y')
		self.updateState(task, job, device)
		self.agent.backward(job)


# print("choice: {}".format(choice))

previousUpdateTime = None
currentTargetIndex = -1


# @staticmethod
def updateOffloadingTarget():
	assert sharedClock is not None

	newTarget = False
	# decide if 
	if offloadingDecision.previousUpdateTime is None:
		sim.debug.out("first round robin")
		# start at the beginning
		offloadingDecision.currentTargetIndex = 0
		newTarget = True
	elif sharedClock >= (offloadingDecision.previousUpdateTime + constants.ROUND_ROBIN_TIMEOUT):
		# print ("next round robin")
		offloadingDecision.currentTargetIndex += 1
		if offloadingDecision.currentTargetIndex >= len(offloadingDecision.options):
			# start from beginning again
			offloadingDecision.currentTargetIndex = 0
		newTarget = True

	# new target has been chosen:
	if newTarget:
		# indicate to old target to process batch immediately
		if offloadingDecision.target is not None:
			sim.debug.out("offloading target", offloadingDecision.target.offloadingDecision)
			# time.sleep(1)
			offloadingDecision.target.addSubtask(sim.subtask.batchContinue(node=offloadingDecision.target))

		offloadingDecision.previousUpdateTime = sharedClock.current
		offloadingDecision.target = offloadingDecision.options[offloadingDecision.currentTargetIndex]

		sim.debug.out("Round robin update: {}".format(offloadingDecision.target), 'r')



# OFFLOAD = action("Offload")


# @staticmethod
# def findAction(targetIndex):


def actionFromIndex(index):
	return offloading.offloadingDecision.possibleActions[index]

# def actionFromTarget(targetIndex):
# 	# find target device for offloading that matches this index
# 	targets = [device for action in possibleActions if action.targetDeviceIndex == targetIndex]
# 	assert len(targets) == 1
# 	return targets[0]
