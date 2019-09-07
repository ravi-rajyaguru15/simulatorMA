import collections 
import datetime 
import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np

import sim.constants

import time 
import os
# print (os.environ["DISPLAY"])
if "DISPLAY" not in os.environ:
	os.environ["DISPLAY"] = "localhost:10.0"
	print("set display to", os.environ["DISPLAY"])
else:
    print ("Existing DISPLAY={}".format(os.environ["DISPLAY"]))

# time.sleep(1)
colours = ['b', 'r']

def plotWithErrors(x, y=None, errors=None, results=None):
	print ("plotting...")
	if y is None:
		y = [result[0] for result in results]
		errors = [result[1] for result in results]

	pp.errorbar(x, y, yerr=errors)
	pp.show()

	
def plotMultiWithErrors(name, results=None, ylim=None, ylabel=None, xlabel=None): # , show=False, save=False):
	print ("plotting!")
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
	pp.grid()
	
	pp.title(name)

	if ylim is not None:
		pp.ylim(ylim)

	if ylabel is not None:
		pp.ylabel(ylabel)

	if xlabel is not None:
		pp.xlabel(xlabel)
		
	if sim.constants.SAVE_GRAPH:
		saveFig(name)

	if sim.constants.DRAW_GRAPH:
		pp.show()

def saveFig(name, unique=False):
	if unique:
		filename = "/output/{}_{}.png".format(name, datetime.datetime.now())
	else:
		filename = "/output/{}.png".format(name)
	try:
		os.mkdir("/output")
	except FileExistsError:
		pass

	print ("saving figure {}".format(filename))
	pp.savefig(filename)