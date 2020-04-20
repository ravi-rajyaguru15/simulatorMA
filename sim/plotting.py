import collections
import datetime
import os
import pickle
import sys

import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np

# print (os.environ["DISPLAY"])
from sim.simulations import constants, localConstants

# if "DISPLAY" not in os.environ:
# 	# os.environ["DISPLAY"] = "localhost:10.0"
# 	os.environ["DISPLAY"] = "/private/tmp/com.apple.launchd.HheW1tn9qY/org.macosforge.xquartz:0"
# 	print("set display to", os.environ["DISPLAY"])
# else:
#     print ("Existing DISPLAY={}".format(os.environ["DISPLAY"]))

# time.sleep(1)
colours = ['b', 'r']

def plotWithErrors(x, y=None, errors=None, results=None):
	print ("plotting...")
	if y is None:
		y = [result[0] for result in results]
		errors = [result[1] for result in results]

	pp.errorbar(x, y, yerr=errors)
	pp.show()


def plotAgentHistory(history):
	print("plotting agent")
	assert history is not None
	filename = "{}{}_{}".format(localConstants.OUTPUT_DIRECTORY, "agentHistory", str(datetime.datetime.now()).replace(":", "."))
	pickle.dump(history, open("{}.pickle".format(filename), "wb"))

	fig, ax1 = pp.subplots()
	ax2 = ax1.twinx()
	legend1, legend2 = [], []
	i = 0
	colours = ['r', 'b', 'g', 'k']
	# create graphs
	negative = False
	for key in history.data:
		graph = np.array(history.getField(key))
		# normalise if required

		if key == 'action':
			func = mpl.axes.Axes.scatter
		else:
			func = mpl.axes.Axes.plot


		if np.max(np.abs(graph)) > 10:
			graph /= np.max(np.abs(graph))
			if np.any(graph < 0):
				negative = True
			
			axis = ax2
			legend2.append(key)
		else:
			axis=ax1
			legend1.append(key)

		# scatter requires different colour
		if func == mpl.axes.Axes.scatter:
			func(axis, np.array(range(len(graph))), graph, c=colours[i])
		else:
			func(axis, np.array(range(len(graph))), graph, colours[i])
		i += 1

	ax1.legend(legend1, loc='lower left')
	ax2.legend(legend2, loc='lower right')
	ax1.set_ylim([0, 1.1 * np.max(history.getField("action"))])
	minimum = -1 if negative else 0
	ax2.set_ylim([minimum, 1])
	pp.grid()
	pp.title("Agent History")
	
	fig.tight_layout()
		
	if localConstants.SAVE_GRAPH:
		saveFig(filename)

	if localConstants.DRAW_GRAPH:
		pp.show()


def plotMultiWithErrors(name, results=None, ylim=None, ylabel=None, xlabel=None,
						separate=False, title=None):  # , show=False, save=False):
	_plotMulti(name, results, ylim, ylabel, xlabel, separate, True, title=title)


def plotMulti(name, results=None, ylim=None, ylabel=None, xlabel=None,
						separate=False, title=None):  # , show=False, save=False):
	_plotMulti(name, results, ylim, ylabel, xlabel, separate, False, title=title)


def _plotMulti(name, results=None, ylim=None, ylabel=None, xlabel=None,
						separate=False, plotErrors=True, title=None):
	# print("plotting!")
	filename = "{}{}_{}".format(localConstants.OUTPUT_DIRECTORY, name, str(datetime.datetime.now()).replace(":", "."))
	pickle.dump((name, results, ylim, ylabel, xlabel), open("{}.pickle".format(filename), "wb"))

	# sort by graph key
	print("results", results)
	orderedResults = collections.OrderedDict(sorted(results.items()))
	print("orderedResults", orderedResults)
	legends = list()
	pp.figure(figsize=(10, 10))
	for key, graph in orderedResults.items():  # , colour in zip(results, colours):
		if separate:
			pp.figure()

		legends.append(key)
		x, y = list(), list()
		errors = list()

		# sort graph by x indices
		# orderedGraph = collections.OrderedDict(sorted(graph.items()))
		# print(graph)

		for xIndex, value in graph.items():
			if isinstance(value, list):
				for yi in value:
					x.append(xIndex)
					y.append(yi)
			else:
				x.append(xIndex)
				y.append(value[0])
				if plotErrors:
					errors.append(value[1])

		sortedY = [k for _,k in sorted(zip(x, y))]
		sortedX = np.sort(x)
		# print(x)
		# print(y)
		# print(np.sort(x))
		# print(sortedY)
		if plotErrors:
			pp.errorbar(sortedX, sortedY, yerr=errors)
		else:
			pp.errorbar(sortedX, sortedY)

	pp.legend(legends)
	pp.grid()

	if title is not None:
		pp.title(title)

	if ylim is not None:
		pp.ylim(ylim)

	if ylabel is not None:
		pp.ylabel(ylabel)

	if xlabel is not None:
		pp.xlabel(xlabel)

	if localConstants.SAVE_GRAPH:
		saveFig(filename)

	if localConstants.DRAW_GRAPH:
		pp.show()

def plotMultiSubplots(name, results=None, ylim=None, ylabel=None, xlabel=None, separate=False, plotErrors=True, subplotCodes=[], scaleJobs=True):
	# print("plotting!")
	filename = "{}{}_{}".format(localConstants.OUTPUT_DIRECTORY, name,
								str(datetime.datetime.now()).replace(":", "."))
	pickle.dump((name, results, ylim, ylabel, xlabel), open("{}.pickle".format(filename), "wb"))

	# sort by graph key
	# print("results", results)
	orderedResults = collections.OrderedDict(sorted(results.items()))
	# print("orderedResults", orderedResults)
	legends = list()
	for i in range(len(subplotCodes)):
		legends.append([])
	pp.figure(figsize=(10, 10))
	print("keys:", orderedResults.keys())
	for key, graph in orderedResults.items():  # , colour in zip(results, colours):
		if separate:
			pp.figure()

		chosenSubplot = None
		# find which subplot to send this to
		for s in range(len(subplotCodes)):
			if subplotCodes[s] in key:
				chosenSubplot = s
				break

		if chosenSubplot is None:
			print("subplot not found!", key, subplotCodes)
		else:
			print("chose", subplotCodes[chosenSubplot], "for", key)
			pp.subplot(1, len(subplotCodes), chosenSubplot + 1)


		legends[chosenSubplot].append(key)
		x, y = list(), list()
		errors = list()

		# sort graph by x indices
		# orderedGraph = collections.OrderedDict(sorted(graph.items()))
		# print(graph)

		for xIndex, value in graph.items():
			if isinstance(value, list):
				for yi in value:
					x.append(xIndex)
					y.append(yi)
			else:
				x.append(xIndex)
				yvalue = value[0]
				yerror = value[1]
				if scaleJobs:
					if "Jobs" in key:
						yvalue *= 1000.
						yerror *= 1000.
				y.append(yvalue)
				if plotErrors:
					errors.append(yerror)

		sortedY = [k for _, k in sorted(zip(x, y))]
		sortedX = np.sort(x)

		if plotErrors:
			pp.errorbar(sortedX, sortedY, yerr=errors)
		else:
			pp.errorbar(sortedX, sortedY)

	for i in range(len(subplotCodes)):
		pp.subplot(1, len(subplotCodes), i+1)
		pp.legend(legends[i])
		pp.grid()
		if ylabel is not None:
			pp.ylabel(ylabel[i])
		pp.tight_layout()
		# pp.title(name)
		if xlabel is not None:
			pp.xlabel(xlabel)



	if ylim is not None:
		pp.ylim(ylim)


	if localConstants.SAVE_GRAPH:
		saveFig(filename)

	if localConstants.DRAW_GRAPH:
		pp.show()

def plotModel(agent, drawLabels=True):
	outputTable = np.zeros((agent.model.stateCount, agent.model.actionCount))
	yticks = []
	for i in range(agent.model.stateCount):
		text = agent.systemState.getStateDescription(i)
		for j in range(agent.model.actionCount):
			outputTable[i, j] = agent.model.getQ(i, j)

		if drawLabels:
			yticks.append(text)
		# pp.text(-2, i, text, horizontalalignment='right', fontsize=5)

	pp.figure(figsize=(10,10))
	pp.title(agent.__name__)

	# normalise:
	outputTable -= constants.INITIAL_Q
	picture = np.zeros((agent.model.stateCount, agent.model.actionCount, 3), dtype=np.float)

	# fig, axes = pp.subplot()
	small, large = np.min(outputTable), np.max(outputTable)
	limit = max(abs(small), abs(large))
	outputTable /= limit


	for i in range(agent.model.stateCount):
		for j in range(agent.model.actionCount):
			current = outputTable[i, j]
			if current < 0:
				picture[i, j] = [-current, 0, 0]
			elif current > 0:
				picture[i, j] = [0, 0, current]

	# print(axes.)
	pp.imshow(picture, aspect=0.5)
	pp.yticks(range(agent.model.stateCount), yticks, fontsize=8)
	pp.xticks(range(agent.model.actionCount), agent.possibleActions, rotation='vertical')
	pp.tight_layout()

	# biggest = max(abs(np.min(outputTable)), abs(np.max(outputTable)))
	# pp.imshow(outputTable, cmap=pp.get_cmap('bwr'))
	pp.show()


def saveFig(filename):
	try:
		os.mkdir(localConstants.OUTPUT_DIRECTORY)
	except FileExistsError:
		pass

	print ("saving figure {}".format(filename))
	pp.savefig("{}.png".format(filename))

def replot(filename):
	# filename = "{}{}_{}".format(localConstants.OUTPUT_DIRECTORY, name,
	# 							str(datetime.datetime.now()).replace(":", "."))
	(name, results, ylim, ylabel, xlabel) = pickle.load(open("{}.pickle".format(filename), "rb"))
	plotMultiSubplots("", results=results, ylim=ylim, ylabel=ylabel, xlabel=xlabel, subplotCodes=["Jobs Devices", "Devices"], plotErrors=True)
	# print("plotting!")

if __name__ == "__main__":
	# fn = sys.argv[1]
	# print("replotting", fn)
	# fn = "DOL_2020-04-20 13.28.20.341042"
	# codes= ["Jobs Devices", "Devices"]
	fn = "DOL_2020-04-20 18.13.58.955317"
	codes = ["Jobs Completed", "DOL"]
	(name, results, ylim, ylabel, xlabel) = pickle.load(open("{}.pickle".format("/tmp/output/simulator/%s" % fn), "rb"))
	plotMultiSubplots(name, results=results, ylim=ylim, ylabel=["System Jobs #", "DOL"], xlabel=xlabel, subplotCodes=codes, plotErrors=True, scaleJobs=True)

