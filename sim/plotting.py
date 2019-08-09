import collections 
import datetime 
import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np

import sim.constants

import os
if "DISPLAY" not in os.environ:
	os.environ["DISPLAY"] = ":3"
	print(os.environ["DISPLAY"])

colours = ['b', 'r']

def plotWithErrors(x, y=None, errors=None, results=None):
	if y is None:
		y = [result[0] for result in results]
		errors = [result[1] for result in results]

	pp.errorbar(x, y, yerr=errors)
	pp.show()

	
def plotMultiWithErrors(name, results=None, ylim=None): # , show=False, save=False):
	print ("plotting!")
	print (results)
	# sort by graph key
	orderedResults = collections.OrderedDict(sorted(results.items()))
	legends = list()
	for key, graph in orderedResults.items(): #, colour in zip(results, colours):
		print (graph)
		legends.append(key)
		x, y = list(), list()
		errors = list()
		
		# sort graph by x indices
		orderedGraph = collections.OrderedDict(sorted(graph.items()))

		for xIndex, value in orderedGraph.items():
			x.append(xIndex)
			y.append(value[0])
			errors.append(value[1])
	
		print (x)
		print (y)
		pp.errorbar(x, y, yerr=errors)
	
	pp.legend(legends)
	
	pp.title(name)

	if ylim is not None:
		pp.ylim(ylim)

	if sim.constants.SAVE:
		saveFig(name)

	if sim.constants.DISPLAY:
		pp.show()

def saveFig(name, unique=False):
	if unique:
		filename = "images/{}_{}.png".format(name, datetime.datetime.now())
	else:
		filename = "images/{}.png".format(name)
	try:
		os.mkdir("images")
	except FileExistsError:
		pass

	print ("saving figure {}".format(filename))
	pp.savefig(filename)