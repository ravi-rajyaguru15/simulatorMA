import sim.constants
# import sim.elasticNode

import warnings
import random

class offloadingDecision:
    options = None
    owner = None

    def __init__(self, device):
        self.owner = device

    @staticmethod
    def selectElasticNodes(devices):
        return [node for node in devices if node.hasFpga()]

    def setOptions(self, allDevices):
        if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.LOCAL_ONLY:
            self.options = [self.owner]
        elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.RANDOM_PEER_ONLY:
            # only offload to something with fpga when needed
            elasticNodes = offloadingDecision.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
            if self.owner in elasticNodes:
                elasticNodes.remove(self.owner)
            self.options = elasticNodes
        elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.SPECIFIC_PEER_ONLY:
            self.options = [allDevices[sim.constants.OFFLOADING_PEER]]
        elif sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.ANYTHING:
            elasticNodes = offloadingDecision.selectElasticNodes(allDevices)  # select elastic nodes from alldevices list]
            self.options = elasticNodes
        else:
            raise Exception("Unknown offloading policy")

        print(sim.constants.OFFLOADING_POLICY, self.owner, self.options)

    def chooseDestination(self, task):
        if self.options is None:
            raise Exception("options are None!")
        elif len(self.options) == 0:
            raise Exception("No options available!")

        # choose randomly from the options available
        # warnings.warn("need to choose differently")
        choice = random.choice(self.options)
        # print (self.options, choice)
        # task.setDestination(choice)

        return choice

        # if constants.OFFLOADING_POLICY == constants.LOCAL_ONLY:
        #     decision = task.host.index
        #     print 'decision', decision
        # else:
        #     choices = 
        #     raise Exception("offloading policy not supported")
        
    