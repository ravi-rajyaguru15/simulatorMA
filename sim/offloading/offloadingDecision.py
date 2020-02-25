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


# print(sim.constants.OFFLOADING_POLICY, self.owner, self.options)

class offloadingDecision:

	simulation = None
	agent = None
	agentClass = None

	def __init__(self, device, systemState, agentClass):
		self.owner = device
		self.systemState = systemState
		self.agentClass = agentClass

# print("choice: {}".format(choice))

previousUpdateTime = None
currentTargetIndex = -1


# @staticmethod

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
