import matplotlib as mpl
mpl.use("QT4Agg")
import matplotlib.pyplot as pp
import pylab
import math

import constants
from elasticNode import elasticNode
from endDevice import endDevice

class visualiser:
    sim = None
    grid = list()
    ax = None
    x,y,width,height = [None] * 4

    def __init__(self, simulator):
        self.sim = simulator

        pp.figure(0)
        pp.xlim(0, 1)
        pp.ylim(0, 1)
        # fig, self.ax = pp.subplots()

        thismanager = pylab.get_current_fig_manager()
        
        # get the QTCore PyRect object
        geom = thismanager.window.geometry()
        self.x,self.y,self.width,self.height = geom.getRect()
        self.moveWindow()

        # thismanager.window.move(-200, 0)
        # thismanager.window.setGeometry(+2400, 400, dx, dy)

        # calculate layout
        print ("*\n*\n*")
        # print ("num devices", len(self.sim.devices))
        rows = math.ceil(math.sqrt(len(self.sim.devices)))
        # print ("rows", rows)
        cols = math.ceil(len(self.sim.devices) / rows)
        # print ("cols", cols)
        if rows * cols < len(self.sim.devices):
            print ("NOT ENOUGH SPACES")

        # vertical spacing 
        # dx = (self.width / (cols + 1))
        dx = 1./(cols + 1)
        # dy = (self.height / (rows + 1))
        dy = 1./(rows + 1)
        y = dy
        for i in range(rows):
            x = dx
            for j in range(cols):
                self.grid.append((x, y))
                x += dx
            y += dy
        
        width, height = [0.15, 0.1]
        # create images for each node
        for dev, location in zip(self.sim.devices, self.grid):
            dev.location = location

            for i in range(len(dev.processors)):
                unit = dev.processors[i]
                unit.createRectangle((dev.location[0] - width/len(dev.processors), dev.location[1]), (width / len(dev.processors), height))

    def update(self):
        # print ("DRAW")
        # self.ax.cla()
        self.drawNodes()
        pp.draw()
        pp.pause(constants.TD)

    def drawNodes(self):
        # print ("drawing nodes:", self.sim.devices)

        for dev, location in zip(self.sim.devices, self.grid):
            self.draw(dev, location)
        
    def draw(self, node, location):
        

        image = list()
        for processor in node.processors:
            rect = processor.rectangle
            if isinstance(node, elasticNode):
                color = (1, 0, 0)
            elif isinstance(node, endDevice):
                color = (0, 0, 0)
            else:
                color = (0, 0, 0)
            rect.fc = color

            image.append(rect)
            # print (node.location)

        for img in image:
            pp.gca().add_patch(img)

    # @staticmethod
    def moveWindow(self):
        thismanager = pylab.get_current_fig_manager()
        thismanager.window.setGeometry(+2400, 400, self.width, self.height)