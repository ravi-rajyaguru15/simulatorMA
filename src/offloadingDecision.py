class offloadingDecision:
    options = None

    def chooseDestination(self, task):
        if self.options is None:
            print "options are None!"

        decision = 0
        
        task.setDestination(self.options[decision])

    