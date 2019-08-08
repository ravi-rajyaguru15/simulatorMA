import datetime 
import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np

import os
os.environ["DISPLAY"] = ":3"
print(os.environ["DISPLAY"])

colours = ['b', 'r']

def plotWithErrors(x, y=None, errors=None, results=None):
	if y is None:
		y = [result[0] for result in results]
		errors = [result[1] for result in results]

	pp.errorbar(x, y, yerr=errors)
	pp.show()

	
def plotMultiWithErrors(x, name, results=None, legend=None, ylim=None, show=False, save=False):
	print (results)
	print (results[0][0])
	for graph in results: #, colour in zip(results, colours):
		y = list()
		errors = list()
	
		for datapoint in graph:
			y.append(datapoint[0])
			errors.append(datapoint[1])
	
		print (x)
		print (y)
		pp.errorbar(x, y, yerr=errors)
	
	if legend is not None:
		pp.legend(legend)
	
	pp.title(name)

	if ylim is not None:
		pp.ylim(ylim)

	if save:
		saveFig(name)

	if show:
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
	pp.savefig(filename)