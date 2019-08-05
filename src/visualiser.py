import matplotlib as mpl
# mpl.use("QT4Agg")
mpl.use("Qt4Agg")
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
	canResize = False

	def __init__(self, simulator):
		self.sim = simulator

		pp.figure(0)
		pp.xlim(0, 1)
		pp.ylim(0, 1)
		# fig, self.ax = pp.subplots()

		thismanager = pylab.get_current_fig_manager()
		
		# get the QTCore PyRect object
		geom = thismanager.window.geometry()
		if isinstance(geom, str):
			print ("STRING")
		else:
			self.canResize = True
			self.x,self.y,self.width,self.height = geom.getRect()
		self.moveWindow()


		grid, _, _ = visualiser.gridLayout(self.sim.devices, (1,1), (.5,.5))
		deviceSize = width, height = [0.2, 0.1]
		
		border = 0.05
		# create images for each node
		for dev, location in zip(self.sim.devices, grid):
			# dev.location = location

			visualiser.createRectangle(dev, (location[0], location[1]), (width + border * 2, height + border * 2), fill=False)

			subgrid, size, (rows, cols) = visualiser.gridLayout(dev.components, deviceSize, location, tight=True)
			for unit, location in zip(dev.components, subgrid):
				# unit = dev.components[i]
				# location = subgrid[i]
				visualiser.createRectangle(unit, (location[0], location[1]), size)

	@staticmethod
	# tight refers to whether there are gaps inbetween 
	def gridLayout(elements, boundingBox, location, tight=False):
		grid = list()
		# calculate layout
		cols = math.ceil(math.sqrt(len(elements)))
		rows = math.ceil(len(elements) / cols)
		
		if rows * cols < len(elements):
			print ("NOT ENOUGH SPACES")

		size = (boundingBox[0] / cols, boundingBox[1] / rows)
		
		# vertical spacing 

		if tight:
			if cols > 1:
				dx = float(size[0]) / (cols - 1)
			else:
				dx = 0
			if rows > 1:
				dy = float(size[1]) / (rows - 1)
			else:
				dy = 0
			y = location[1] - boundingBox[1]  + dy/2
		else:
			dx = float(boundingBox[0])/(cols + 1)
			dy = float(boundingBox[1])/(rows + 1)
			y = location[1] - boundingBox[1]/2
		
		# x, y start on corners
		for i in range(rows):
			y += dy

			if tight:
				x = location[0] - boundingBox[0]/2 - size[0] / 2
			else:
				x = location[0] - boundingBox[0]/2
				
			for j in range(cols):
				x += dx

				grid.append((x, y))
		
		return grid, size, (rows, cols)

	def update(self):
		# print ("DRAW")
		# self.ax.cla()
		self.drawNodes()
		pp.draw()
		pp.pause(constants.TD)

	@staticmethod
	def createRectangle(targetDevice, location, size, fill=True):
		targetDevice.rectangle = pp.Rectangle((location[0] - size[0]/2, location[1] - size[1]/2), size[0], size[1], fill=fill)
	

	def drawNodes(self):
		# print ("drawing nodes:", self.sim.devices)

		# for dev, location in zip(self.sim.devices, self.grid):
		for dev in self.sim.devices:
			self.draw(dev)
		
	def draw(self, node):
		
		try:
			image = list()
			# draw node itself
			# change colour of border based on activity
			node.rectangle._edgecolor = (1, 0, 0, 1) if node.busy() else (0, 0, 0, 1)
			image.append(node.rectangle)

			# draw all processors and wireless
			for component in node.components:
				rectangle = component.rectangle
				if component.busy:
					colour = component.busyColour
				else:
					colour = component.idleColour
				
				rectangle._facecolor = colour
				image.append(rectangle)
				
			for img in image:
				pp.gca().add_patch(img)
		except RuntimeError:
			print ("Drawing failed")
			self.sim.finished = True

	# @staticmethod
	def moveWindow(self):
		if self.canResize:
			thismanager = pylab.get_current_fig_manager()
			thismanager.window.setGeometry(+2400, 400, self.width, self.height)