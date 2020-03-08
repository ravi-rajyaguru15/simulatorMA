import collections
import datetime
import os
import pickle

import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np

import sim.simulations.constants

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
						separate=False):  # , show=False, save=False):
	_plotMulti(name, results, ylim, ylabel, xlabel, separate, True)


def plotMulti(name, results=None, ylim=None, ylabel=None, xlabel=None,
						separate=False):  # , show=False, save=False):
	_plotMulti(name, results, ylim, ylabel, xlabel, separate, False)


def _plotMulti(name, results=None, ylim=None, ylabel=None, xlabel=None,
						separate=False, plotErrors=True):
	# print("plotting!")
	filename = "{}{}_{}".format(localConstants.OUTPUT_DIRECTORY, name, str(datetime.datetime.now()).replace(":", "."))
	pickle.dump((name, results, ylim, ylabel, xlabel), open("{}.pickle".format(filename), "wb"))

	# sort by graph key
	orderedResults = collections.OrderedDict(sorted(results.items()))
	legends = list()
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

		if plotErrors:
			pp.errorbar(x, y, yerr=errors)
		else:
			pp.errorbar(x, y)

	pp.legend(legends)
	pp.grid()

	pp.title(name)

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


def saveFig(filename):
	try:
		os.mkdir(localConstants.OUTPUT_DIRECTORY)
	except FileExistsError:
		pass

	print ("saving figure {}".format(filename))
	pp.savefig("{}.png".format(filename))

