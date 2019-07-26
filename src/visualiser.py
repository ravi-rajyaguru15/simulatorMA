import matplotlib.pyplot as pp

class visualiser:
    sim = None

    def __init__(self, simulator):
        self.sim = simulator

    def update(self):
        print "updating"
