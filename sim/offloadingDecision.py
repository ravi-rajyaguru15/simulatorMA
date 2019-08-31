import sim.constants
import sim.debug
# import sim.elasticNode

import warnings
import random
import time
import numpy as np

class offloadingDecision:
	options = None
	owner = None
	target = None

	def __init__(self, device):
		self.owner = device

	@staticmethod
	def selectElasticNodes(devices):
		return [node for node in devices if node.hasFpga()]

	def setOptions(self, allDevices):
		# set options for all policies that use it, or select constant target
		if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.LOCAL_ONLY:
			self.target = self.owner
		elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.RANDOM_PEER_ONLY:
			# only offload to something with fpga when needed
			elasticNodes = offloadingDecision.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
			if self.owner in elasticNodes:
				elasticNodes.remove(self.owner)
			self.options = elasticNodes
		elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.SPECIFIC_PEER_ONLY:
			self.target = allDevices[sim.constants.OFFLOADING_PEER]
		elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.ANYTHING:
			self.options = offloadingDecision.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
		elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.ANNOUNCED:
			self.options = offloadingDecision.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
			# self.target = self.owner
		else:
			raise Exception("Unknown offloading policy")

		# print(sim.constants.OFFLOADING_POLICY, self.owner, self.options)

	def chooseDestination(self, task):
		# if specified target, return it
		if self.target is not None:
			return self.target
		elif self.options is None:
			raise Exception("options are None!")
		elif len(self.options) == 0:
			raise Exception("No options available!")
		else:
			# choose randomly from the options available
			# warnings.warn("need to choose differently")
			if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.ANNOUNCED:
				# every other offloading policy involves randoming
				batches = np.array([len(dev.batch[task]) if task in dev.batch.keys() else 0 for dev in self.options])
				# is the config already available?
				configsAvailable = np.array([dev.fpga.currentConfig == task for dev in self.options])

				decisionFactors = batches + configsAvailable

				# nobody has a batch going
				if np.sum(decisionFactors) == 0:
					# then have to do it yourself
					choice = self.owner
				else:
					largestBatches = np.argmax(decisionFactors)
					# print('largest:', largestBatches)
					choice = self.options[largestBatches]

			else:
				choice = random.choice(self.options)
			# print (self.options, choice)
			# task.setDestination(choice)
			sim.debug.out("Job assigned: {} -> {}".format(self.owner, choice))
			# time.sleep(1)
			return choice

		# if constants.OFFLOADING_POLICY == constants.LOCAL_ONLY:
		#     decision = task.host.index
		#     print 'decision', decision
		# else:
		#     choices = 
		#     raise Exception("offloading policy not supported")
		
	