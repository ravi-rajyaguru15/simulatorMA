import os
# print("DISPLAY:",os.environ["DISPLAY"])
# import matplotlib as mpl
# mpl.use("Qt5Agg")
import traceback
# mpl.use("QT4Agg")
# oldBackend = mpl.get_backend()
# print("existing", oldBackend)

import sys
# if sys.platform != 'darwin':
# 	try:
# 		mpl.use("TkAgg")
# 		# mpl.use("Qt5Agg")
# 	except ImportError as i:
# 		mpl.use(oldBackend)
# 		print(i)
# 		print("Cannot import MPL backend")
import matplotlib.pyplot as pp
# pp.switch_backend("tkagg")
import pylab
import math
import time
import numpy as np
import datetime
# import sys
# sys.exit(0)
import sim.constants
import sim.offloadingDecision
from sim.elasticNode import elasticNode
from sim.endDevice import endDevice
import sim.plotting

DEVICE_SIZE = [0.2, 0.1]
TEXT_SPACING = 0.05
BORDER = 0.05
DEVICES_FIGURE = 5
DEVICES_ENERGY_FIGURE = 2
DEVICES_POWER_FIGURE = 3
SUBTASKS_DURATIONS_FIGURE = 4
DEVICES_LIFETIME_FIGURE = 5

class visualiser:
	# sim = None
	grid = list()
	ax = None
	x,y,width,height = [None] * 4
	canResize = False
	clock = None
	devices = None
	devicesNames = None
	totalDevicesEnergyFunction = None
	completedJobs = None

	def __init__(self, simulation):
		# self.sim = simulator
		self.setSimulation(simulation)

		if sim.constants.DRAW_DEVICES:
			print ("Creating 1")
			pp.figure(DEVICES_FIGURE)
			# pp.xlim(0, 1)
			# pp.ylim(0, 1)

		if sim.constants.DRAW_GRAPH_TOTAL_ENERGY:
			print ("Creating 2")
			pp.figure(DEVICES_ENERGY_FIGURE)
			pp.xlim(0, len(self.devices))

		if sim.constants.DRAW_GRAPH_CURRENT_POWER:
			print ("Creating 3")
			
			pp.figure(DEVICES_POWER_FIGURE)
			pp.xlim(0, len(self.devices))
		# fig, self.ax = pp.subplots()
		
		if sim.constants.DRAW_GRAPH_EXPECTED_LIFETIME:
			pp.figure(DEVICES_LIFETIME_FIGURE)

		if sim.constants.DRAW_DEVICES:
			thismanager = pylab.get_current_fig_manager()
			
			try:
				# get the QTCore PyRect object
				geom = thismanager.window.geometry()
				if isinstance(geom, str):
					print("STRING")
				else:
					self.canResize = True
					self.x,self.y,self.width,self.height = geom.getRect()
				self.moveWindow()
			except AttributeError:
				print("Cannot modify QT window")


			grid, _, _ = visualiser.gridLayout(self.devices)
			deviceSize = width, height = DEVICE_SIZE
			
			# create images for each node
			for dev, location in zip(self.devices, grid):
				# dev.location = location

				# node drawing
				visualiser.createRectangle(dev, (location[0], location[1]), (width + BORDER * 2, height + BORDER * 2), fill=False)
				# visualiser.createText(dev, (location[0], location[1]))

				# component drawing
				subgrid, size, (rows, cols) = visualiser.gridLayout(dev.components, deviceSize, location, tight=True)
				for unit, location in zip(dev.components, subgrid):
					# unit = dev.components[i]
					# location = subgrid[i]
					visualiser.createRectangle(unit, (location[0], location[1]), size)

	def setSimulation(self, simulation):
		self.clock = simulation.time
		self.devices = simulation.devices
		self.devicesNames = simulation.devicesNames()
		self.totalDevicesEnergyFunction = simulation.totalDevicesEnergy
		self.completedJobs = simulation.getCompletedJobs

	@staticmethod
	# tight refers to whether there are gaps inbetween 
	def gridLayout(elements, boundingBox=None, location=None, tight=False):
		square = math.sqrt(len(elements))
		if boundingBox is None:
			boundingBox = (square, square)
		
		if location is None:
			location = (boundingBox[0]/2, boundingBox[1]/2)
		
		grid = list()
		# calculate layout
		cols = math.ceil(square)
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

		if sim.constants.DRAW_DEVICES:
			self.drawNodes()
			pp.draw()
			# if sim.constants.SAVE:
			# 	sim.plotting.saveFig("devices")

		if sim.constants.DRAW_GRAPH_TOTAL_ENERGY:
			self.drawTotalDeviceEnergy()
			pp.draw()

		if sim.constants.DRAW_GRAPH_SUBTASK_DURATION:
			self.drawSubtaskDuration()
			pp.draw()
		
		if sim.constants.DRAW_GRAPH_CURRENT_POWER:
			self.drawCurrentDevicePower()
			pp.draw()

		if sim.constants.DRAW_GRAPH_EXPECTED_LIFETIME:
			self.drawExpectedLifetimes()
			pp.draw
		
		
		pp.pause(1e-6) # sim.constants.TD)

	@staticmethod
	def createRectangle(targetDevice, location, size, fill=True):
		targetDevice.location = location
		targetDevice.rectangle = pp.Rectangle((location[0] - size[0]/2, location[1] - size[1]/2), size[0], size[1], fill=fill)
	# @staticmethod 
	# def createText(targetDevice, location):
	
	# 	targetDevice.title = pp.Text(x=location[0], y=location[1], horizontalalignment='center')
	def drawTotalDeviceEnergy(self):
		
		energyList = self.totalDevicesEnergyFunction() # self.sim.totalDevicesEnergy()
		
		pp.figure(DEVICES_ENERGY_FIGURE)
		pp.bar(np.array(range(len(self.devices))) + 0.5, energyList, tick_label=self.devicesNames, color=['b'] * len(self.sim.devices))
		
	def drawSubtaskDuration(self):
		subtasks = [
			sim.subtask.batchContinue, 
			sim.subtask.batching, 
			sim.subtask.createMessage,
			sim.subtask.fpgaMcuOffload, 
			sim.subtask.mcuFpgaOffload,
			sim.subtask.newJob,
			sim.subtask.processing, 
			sim.subtask.reconfigureFPGA,
			sim.subtask.rxJob,
			sim.subtask.rxResult,
			sim.subtask.txJob,
			sim.subtask.txMessage
			]

		pp.figure(SUBTASKS_DURATIONS_FIGURE)
		pp.cla()
		durations = [task.totalDuration for task in subtasks]
		xs = np.array(range(len(subtasks))) + 0.5
		pp.bar(xs, durations, color=['b'] * len(subtasks))
		pp.xticks(xs, [task.__name__ for task in subtasks], rotation='vertical')

	
	maxPowerEver = 0.5
	def drawCurrentDevicePower(self):
		labels = self.sim.devicesNames()
		powerList = self.sim.currentDevicesEnergy()

		maxPower = np.max(powerList)
		self.maxPowerEver = np.max([self.maxPowerEver, maxPower])
		print (powerList)
		
		pp.figure(DEVICES_POWER_FIGURE)
		pp.cla()
		pp.bar(np.array(range(len(self.sim.devices))) + 0.5, powerList, tick_label=labels, color=['b'] * len(self.sim.devices))
		pp.ylim(0, self.maxPowerEver * 1.1)
	

	def drawExpectedLifetimes(self):
		labels = self.sim.devicesNames()
		
		LIMIT = int(1e3 / sim.constants.TD)
		
		if LIMIT is not None:
			# before = datetime.datetime.now()
			if len(self.sim.lifetimes) > LIMIT:
				self.sim.timestamps = self.sim.timestamps[-LIMIT:]
				self.sim.lifetimes = self.sim.lifetimes[-LIMIT:]
				self.sim.energylevels = self.sim.energylevels[-LIMIT:]
			# print((datetime.datetime.now() - before).total_seconds())
			
		# pp.figure(DEVICES_LIFETIME_FIGURE)
		fig, ax1 = pp.subplots(num=DEVICES_LIFETIME_FIGURE)
		fig.clf()
		pp.title("Expected Life {}".format(self.sim.time))
		pp.plot(self.sim.timestamps, self.sim.lifetimes, 'b')
		pp.ylabel("Lifetimes (in s)")
		pp.grid()
		ax2 = pp.twinx()
		ax2.plot(self.sim.timestamps, self.sim.energylevels, 'r')
		ax2.set_ylabel("EnergyLevels (in J)")
		# ax2 = ax1.twinx()
		# ax2.cla()
		# ax2.plot(self.energylevels)
		# ax2.set_ylabel("EnergyLevels (in J)")
		# .legend(["Lifetimes", "EnergyLevels"])


	def drawNodes(self):
		# print ("drawing nodes:", self.sim.devices)

		pp.figure(DEVICES_FIGURE)
		pp.cla()
		if sim.constants.OFFLOADING_POLICY == sim.offloadingPolicy.ROUND_ROBIN:
			roundRobinText = ", {}".format(sim.offloadingDecision.currentSubtask.target)
		else:
			roundRobinText = ""
		pp.title("Time = {}, TotalSleep = {:.3f}, TotalJobs {:d}, AveragePower {:.3f}{}".format(self.clock, np.average([dev.totalSleepTime for dev in self.devices]), self.completedJobs(), np.average(self.totalDevicesEnergyFunction()) / self.clock.current, roundRobinText))
		# for dev, location in zip(self.sim.devices, self.grid):
		for dev in self.devices:
			self.draw(dev)
		
		# limits
		xlimits = (-DEVICE_SIZE[0] - BORDER * 4 + np.min([dev.location[0] for dev in self.devices]), DEVICE_SIZE[0] + BORDER * 4 + np.max([dev.location[0] for dev in self.devices]))
		ylimits = (-DEVICE_SIZE[1] - BORDER * 4 + np.min([dev.location[1] for dev in self.devices]), DEVICE_SIZE[1] + BORDER * 4 + np.max([dev.location[1] for dev in self.devices]))

		# print(np.min([xlimits[0], 0]))
		# print(np.max([xlimits[1], 1]))
		# pp.xlim(np.min([xlimits[0], 0]), np.max([xlimits[1], 1]))
		# pp.ylim(np.min([ylimits[0], 0]), np.max([ylimits[1], 1]))
		pp.xlim(xlimits)
		pp.ylim(ylimits)

	def draw(self, node):
		try:
			image = list()
			# draw node itself
			# change colour of border based on activity
			node.rectangle._edgecolor = (1, 0, 0, 1) if node.hasJob() else (0, 0, 0, 1)
			image.append(node.rectangle)

			# update node's title to current description
			top = node.location[1] + node.rectangle.get_height()/2
			pp.gca().text(x=node.location[0], y=top + TEXT_SPACING * 3, s="{} ({})".format(node, node.maxBatchLength()[0]), verticalalignment='center', horizontalalignment='center')
			pp.gca().text(x=node.location[0], y=top + TEXT_SPACING * 2, s=node.currentBatch, verticalalignment='center', horizontalalignment='center')
			pp.gca().text(x=node.location[0], y=top + TEXT_SPACING * 1, s=node.currentSubtask, verticalalignment='center', horizontalalignment='center')

			# draw all processors and wireless
			for component in node.components:
				rectangle = component.rectangle
								
				rectangle._facecolor = component.colour()
				image.append(rectangle)
				
			for img in image:
				pp.gca().add_patch(img)
		except RuntimeError:
			print ("Drawing failed")
			# traceback.print_exc()
			sim.simulation.current.finished = True

	# @staticmethod
	def moveWindow(self):
		if self.canResize:
			thismanager = pylab.get_current_fig_manager()
			thismanager.window.setGeometry(+2400, 400, self.width, self.height)
