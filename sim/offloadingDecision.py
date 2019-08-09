import sim.constants

import warnings
import random

class offloadingDecision:
    options = None

    def chooseDestination(self, task):
        if self.options is None:
            print ("options are None!")
        elif len(self.options) == 0:
            print ("No options available!")

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
        
    