import collections
import datetime
import os
import pickle
import sys
from _signal import pause
from os import wait
from time import time

import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np

# print (os.environ["DISPLAY"])
import tikzplotlib as tikzplotlib
import os
# print()
# print(os.path.abspath(os.curdir))
# print(sys.path)
# print()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
						separate=False, title=None, logx=False, legend=None, order=True, legendlocation='best'):
	_plotMulti(name, results, ylim, ylabel, xlabel, separate, True, title=title, logx=logx, legend=legend, order=order, legendlocation=legendlocation)


def plotMultiSeparate(name, results=None, ylim=None, ylabel=None, xlabel=None,
						separate=False, title=None, logx=False, legend=None, order=True, legendlocation='best'):
	_plotMulti(name, results, ylim, ylabel, xlabel, separate, False, title=title, logx=logx, legend=legend, order=False, legendlocation=legendlocation)


figsize = (8, 8)
def _plotMulti(name, results=None, ylim=None, ylabel=None, xlabel=None,
						separate=False, plotErrors=True, title=None, logx=False, legend=None, order=True, subplots=False, subplotCodes=[], legendlocation='best', saveTimestamp=False):
	# print("plotting!")
	if saveTimestamp:
		filename = f"{localConstants.OUTPUT_DIRECTORY}{name}_{str(datetime.datetime.now())}".replace(":", ".")
	else:
		filename = f"{localConstants.OUTPUT_DIRECTORY}{name}".replace(":", ".")

		# filename = "{}{}_{}".format(localConstants.OUTPUT_DIRECTORY, name, str(datetime.datetime.now()).replace(":", "."))
	try:
		os.makedirs(localConstants.OUTPUT_DIRECTORY, exist_ok=True)
	except FileExistsError:
		pass
	pickle.dump((name, results, ylim, ylabel, xlabel), open("{}.pickle".format(filename), "wb"))

	# sort by graph key
	print("results", results)

	alreadysorted = False
	if legend is not None:
		if isinstance(legend, tuple):
			print("manually reorder")
			newdict = dict()
			keys = np.array(list(results.keys()))
			# print("orig", keys)
			# print(legend[1])
			keys = keys[legend[1]]
			for key in keys:
				# print(key)
				newdict[key] = results[key]
			orderedResults = newdict
			alreadysorted = True

			items = orderedResults.items()
			keys = orderedResults.keys()
			# print("keys", keys)
			# print(legend[1])
			# print(items)

	if not alreadysorted:
		if order:
			orderedResults = collections.OrderedDict(sorted(results.items()))
		else:
			orderedResults = results

		items = orderedResults.items()

	# print("orderedResults", orderedResults)
	legends = list()
	for i in range(len(subplotCodes)): legends.append(list())
	if not separate and not subplots:
		pp.figure(figsize=figsize)

	elif separate:
		for i in range(len(subplotCodes)):
			pp.figure(i, figsize=figsize)


	for i, (key, graph) in zip(range(len(orderedResults.keys())), items):  # , colour in zip(results, colours):
		# print("key", key)
		# if separate:
		# 	pp.figure()

		# choose subplot or figure:
		if separate or subplots:
			chosenSubplot = None
			# find which subplot to send this to
			for s in range(len(subplotCodes)):
				if subplotCodes[s] in key:
					chosenSubplot = s
					break

			if chosenSubplot is None:
				print("subplot not found!", key, subplotCodes)
			elif not separate:
				print("chose", subplotCodes[chosenSubplot], "for", key)
				pp.subplot(1, len(subplotCodes), chosenSubplot + 1)
			else:
				# print("creating figure '%d'" % chosenSubplot)
				pp.figure(chosenSubplot) # , figsize=(10, 10))

			if legend is None:
				legends[chosenSubplot].append(key)
			else:
				legends[chosenSubplot].append(legend[0][i])

		else:
			legends.append(key)
			
		x, y = list(), list()
		errors = list()

		# sort graph by x indices
		# orderedGraph = collections.OrderedDict(sorted(graph.items()))
		# print(graph)

		for xIndex, value in graph.items():
			# print(xIndex, value)
			if isinstance(value, list):
				for yi in value:
					x.append(xIndex)
					y.append(yi)
			else:
				x.append(xIndex)
				y.append(value[0])
				if plotErrors:
					if isinstance(value[1], np.ndarray):
						# TODO: no idea why this is an array
						print("warning: errors are an array")
						errors.append(np.average(value[1]))
					else:
						errors.append(value[1])
				# print(xIndex, value[0], value[1])

		# print(x)
		# print(y)
		sortedY = [k for _,k in sorted(zip(x, y))]
		if plotErrors:
			sortedErrors = [k for _,k in sorted(zip(x, errors))]
		sortedX = np.sort(x)
		# print(x)
		# print(y)
		# print(np.sort(x))
		# print(sortedY)

		# print("plotting", key, "on", chosenSubplot)
		# pp.title("drawing %d" % chosenSubplot)
		if logx:
			pp.xscale("log", nonposx='clip')
		if plotErrors:
			# print("errors:", sortedErrors)
			if len(errors) == 0:
				print("FAKING ERRORS!!")
				sortedErrors = np.zeros_like(np.array(sortedY))
			pp.errorbar(sortedX, sortedY, yerr=sortedErrors)
			# print(key, sortedX, sortedY, sortedErrors)
		else:
			pp.errorbar(sortedX, sortedY)

	if separate or subplots:
		for i in range(len(subplotCodes)):
			# print("creating figure for", subplotCodes[i])
			if separate:
				# print("rendering figure '%d'" % i)
				pp.figure(i) # , figsize=(10,10))
			else:
				pp.subplot(1, len(subplotCodes), i+1)


			if legend is None:
				# print("legends:",legends)
				pp.legend(legends[i], loc=legendlocation)
			elif not isinstance(legend, tuple):
				pp.legend(legend, loc=legendlocation)
			elif isinstance(legend[0][0], list):
				print("given new legends")
				pp.legend(legend[0][i], legendlocation)
			else:
				pp.legend(legends[i], legendlocation)
			pp.grid()
			if ylabel is not None:
				pp.ylabel(ylabel[i])
			pp.tight_layout()
			# pp.title("figure %d" % i)
			if xlabel is not None:
				pp.xlabel(xlabel)

			if localConstants.SAVE_GRAPH:
				saveFig("%s-%d" % (filename, i))

		if localConstants.DRAW_GRAPH:
			# print ("showing", i)
			pp.show()
	else:
		# if legend is None or isinstance(legend, tuple):
		# 	pp.legend(legends, loc='best')
		# else:
		# 	pp.legend(legend)
		if legend is None:
			# print("legends:",legends)
			pp.legend(legends, loc=legendlocation)
		elif not isinstance(legend, tuple):
			pp.legend(legend, loc=legendlocation)
		elif isinstance(legend[0], list):
			print("given new legends")
			legend[0].sort()
			pp.legend(legend[0], loc=legendlocation)
		else:
			pp.legend(legends, loc=legendlocation)
		pp.grid()

		if title is not None:
			pp.title(title)

		if ylim is not None:
			pp.ylim(ylim)

		if ylabel is not None:
			pp.ylabel(ylabel)

		if xlabel is not None:
			pp.xlabel(xlabel)

		pp.tight_layout()
		if localConstants.SAVE_GRAPH:
			saveFig(filename)

		if localConstants.DRAW_GRAPH:
			pp.show()


def plotMultiSubplots(name, results=None, ylim=None, ylabel=None, xlabel=None, plotErrors=True,
					  subplotCodes=[], legend=None, scaleJobs=True):
	_plotMulti(name=name, results=results, ylim=ylim, ylabel=ylabel, xlabel=xlabel, separate=False, legend=legend,
			  subplotCodes=subplotCodes, plotErrors=plotErrors, subplots=True)

def plotMultiSeparate(name, results=None, ylim=None, ylabel=None, xlabel=None, plotErrors=True,
					  subplotCodes=[], legend=None, scaleJobs=True):
	_plotMulti(name=name, results=results, ylim=ylim, ylabel=ylabel, xlabel=xlabel, separate=True, legend=legend,
			  subplotCodes=subplotCodes, plotErrors=plotErrors, subplots=False)

	# # print("plotting!")
	# filename = "{}{}_{}".format(localConstants.OUTPUT_DIRECTORY, name,
	# 							str(datetime.datetime.now()).replace(":", "."))
	# try:
	# 	os.makedirs(localConstants.OUTPUT_DIRECTORY, exist_ok=True)
	# except FileExistsError:
	# 	pass
	# pickle.dump((name, results, ylim, ylabel, xlabel), open("{}.pickle".format(filename), "wb"))
	#
	# # sort by graph key
	# # print("results", results)
	# orderedResults = collections.OrderedDict(sorted(results.items()))
	# # print("orderedResults", orderedResults)
	# legends = list()
	# for i in range(len(subplotCodes)):
	# 	legends.append([])
	# pp.figure(figsize=(10, 10))
	# print("keys:", orderedResults.keys())
	# for key, graph in orderedResults.items():  # , colour in zip(results, colours):
	# 	# if separate:
	# 	# 	pp.figure(figsize=(10, 10))
	#
	# 	chosenSubplot = None
	# 	# find which subplot to send this to
	# 	for s in range(len(subplotCodes)):
	# 		if subplotCodes[s] in key:
	# 			chosenSubplot = s
	# 			break
	#
	# 	if chosenSubplot is None:
	# 		print("subplot not found!", key, subplotCodes)
	# 	elif not separate:
	# 		print("chose", subplotCodes[chosenSubplot], "for", key)
	# 		pp.subplot(1, len(subplotCodes), chosenSubplot + 1)
	# 	else:
	# 		pp.figure(chosenSubplot, figsize=(10, 10))
	#
	#
	# 	legends[chosenSubplot].append(key)
	# 	x, y = list(), list()
	# 	errors = list()
	#
	# 	# sort graph by x indices
	# 	# orderedGraph = collections.OrderedDict(sorted(graph.items()))
	# 	# print(graph)
	#
	# 	for xIndex, value in graph.items():
	# 		if isinstance(value, list):
	# 			for yi in value:
	# 				x.append(xIndex)
	# 				y.append(yi)
	# 		else:
	# 			x.append(xIndex)
	# 			yvalue = value[0]
	# 			yerror = value[1]
	# 			if scaleJobs:
	# 				if "Jobs" in key:
	# 					yvalue *= 1000.
	# 					yerror *= 1000.
	# 			y.append(yvalue)
	# 			if plotErrors:
	# 				errors.append(yerror)
	#
	# 	sortedY = [k for _, k in sorted(zip(x, y))]
	# 	sortedX = np.sort(x)
	#
	# 	if plotErrors:
	# 		pp.errorbar(sortedX, sortedY, yerr=errors)
	# 	else:
	# 		pp.errorbar(sortedX, sortedY)
	#
	# for i in range(len(subplotCodes)):
	# 	if separate:
	# 		pp.figure(i)
	# 	else:
	# 		pp.subplot(1, len(subplotCodes), i+1)
	# 	pp.legend(legends[i])
	# 	pp.grid()
	# 	if ylabel is not None:
	# 		pp.ylabel(ylabel[i])
	# 	pp.tight_layout()
	# 	# pp.title(name)
	# 	if xlabel is not None:
	# 		pp.xlabel(xlabel)


	#
	# if ylim is not None:
	# 	pp.ylim(ylim)
	#
	#
	# if localConstants.SAVE_GRAPH:
	# 	saveFig(filename)
	#
	# if localConstants.DRAW_GRAPH:
	# 	pp.show()

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
	if localConstants.SAVE_GRAPH:
		filename = "%s/agent %s model (%s)" % (localConstants.OUTPUT_DIRECTORY, agent.__name__, str(datetime.datetime.now()).replace(":", "."))
		saveFig(filename)

	if localConstants.DRAW_GRAPH:
		print("DRAWING GRAPH")
		pp.show()

def saveFig(filename):
	# try:
	os.makedirs(localConstants.OUTPUT_DIRECTORY, exist_ok=True)
	# except FileExistsError:
	# 	pass

	print ("saving figure {}".format(filename))
	children = [c for c in [child.get_children() for child in pp.gcf().get_children()]][1]
	legends = [c for c in children if isinstance(c, mpl.legend.Legend)]
	legend = legends[0].get_texts()
	legendTexts = [a for a in legend]
	# print("found", legendTexts)
	tikz = tikzplotlib.get_tikz_code().split('\n')
	# print(tikz)
	index = 0
	# print("total length = " + str(len(tikz)))
	for i in range(len(legendTexts)):
		# print("finding " + str(i) + " " + legendTexts[i].get_text())

		# finding next legend entry...
		for j in range(index, len(tikz)):
			if 'addlegendentry' in tikz[j]:
				break

		newline = '\\addlegendentry{' + legendTexts[i].get_text() + '}'
		tikz[j] = newline
		index = j+1

	open("{}.tex".format(filename), 'w').writelines([line + '\n' for line in tikz])

	# tikzplotlib.save("{}.tex".format(filename))
	# result = open("{}.tex".format(filename)).readlines()
	# print("legends:")
	# for i in [line for line in result if 'addlegendentry' in line]:
	# 	print (i)
	pp.savefig("{}.png".format(filename))

def replot(filename):
	# filename = "{}{}_{}".format(localConstants.OUTPUT_DIRECTORY, name,
	# 							str(datetime.datetime.now()).replace(":", "."))
	(name, results, ylim, ylabel, xlabel) = pickle.load(open("{}.pickle".format(filename), "rb"))
	plotMultiSubplots("", results=results, ylim=ylim, ylabel=ylabel, xlabel=xlabel, subplotCodes=["Jobs Devices", "Devices"], plotErrors=True)
	# print("plotting!")

acsos = "/Users/alwynburger/git/acsos-2020/figures/extra data"

def replotexp1():
	fn = "experiment1_2020-04-28 14.02.09.563071"
	(name, results, ylim, ylabel, xlabel) = pickle.load(open("{}/{}.pickle".format(acsos, fn), "rb"))
	legend = results.keys()
	newlegend = []
	print("legend:", legend)
	import scanf
	for l in legend:
		print(l)
		central = None
		if "Centralised" in l:
			if "Random" in l:
				agent = "Random"
			else:
				agent = scanf.scanf("%s Table Agent Centralised", l)[0]
			central = "Centralised"
		else:
			agent = scanf.scanf("%s Table Agent Decentralised", l)[0]
			central = "Decentralised"

		if agent == "Minimal": agent = "Basic"

		print("'%s'" % agent)

		if "Random" in agent:
			s = "%s Agent" % agent
		else:
			s = "%s Table Agent %s" % (agent, central)
		# s = "%s %% Basic Agents" % perc
		# print(perc, "'%s'"%s)
		newlegend.append(s)

	neworder = np.argsort(newlegend)
	# neworder = neworder[::-1]
	print(neworder)
	plotMultiWithErrors(name, results, ylim, ylabel="Average Jobs", xlabel=xlabel.replace('#', '\\#'), legend=(newlegend, neworder), order=False)


def replotexp3():
	fn = "Max Jobs in Queue_2020-04-24 18.06.33.201307"
	(name, results, ylim, ylabel, xlabel) = pickle.load(open("{}/{}.pickle".format(acsos, fn), "rb"))
	legend = results.keys()
	newlegend = []
	print("legend:", legend)
	import scanf
	for l in legend:
		print(l)
		agent = scanf.scanf("Agent %s Table Agent", l)[0]

		if agent == "Minimal": agent = "Basic"

		print("'%s'" % agent)

		s = "%s Table Agent" % (agent)
		# s = "%s %% Basic Agents" % perc
		# print(perc, "'%s'"%s)
		newlegend.append(s)

	neworder = np.argsort(newlegend)
	# neworder = neworder[::-1]
	print(neworder)
	plotMultiWithErrors(name, results, ylim, ylabel="Average Jobs", xlabel=xlabel, legend=(newlegend, neworder), order=False, logx=True, legendlocation='lower left')


def replotexp4():
	fn = "experiment4normalised_2020-04-28 16.12.54.347130"
	(name, results, ylim, ylabel, xlabel) = pickle.load(open("{}/{}.pickle".format(acsos, fn), "rb"))
	codes = ["Jobs Completed", "DOL"]
	legend = results.keys()
	newlegend = []
	newlegends = []
	for i in range(len(codes)): newlegends.append([])
	# print("legend:", legend)
	import scanf
	scans = ["%s %%d devices" % code for code in codes]

	for l in legend:
		# print(l)
		for i, s in zip(range(len(scans)), scans):
			result = scanf.scanf(s, l)
			if result is None: continue

			perc = str((scanf.scanf(s, l))[0])
			perc = perc.rjust(2)
			print(perc)
			s = "%s devices" % perc
			newlegend.append(s)
			newlegends[i].append(s)

	# for i in range(len(scans)): newlegends[i].sort()
	print("newlegend", newlegend)
	neworder = np.argsort(newlegend)
	neworder = neworder[::-1]
	print("new order:", neworder)
	newlegend = newlegend[::-1]

	plotMultiSeparate(name, results=results, ylim=ylim, ylabel=["System Jobs \\#", "DOL"], xlabel=xlabel.replace('#', '\\#'),
					  legend=(newlegend, neworder), subplotCodes=codes, plotErrors=True, scaleJobs=False)


def replotexp5():
	fn = "Competing Agents_2020-05-02 10.53.18.075400"
	# fn = "Competing Agents_2020-05-02 15.10.58.898751"
	(name, results, ylim, ylabel, xlabel) = pickle.load(open("{}/{}.pickle".format(acsos, fn), "rb"))
	legend = results.keys()
	newlegend = []
	print("legend:", legend)
	import scanf
	for l in legend:
		print(l)
		perc = (scanf.scanf("%d %s Basic Agents", l))[0]
		num = int(10. * int(perc * 10 / 100))
		print("correcting percentage:", perc, num)
		perc = str(num).rjust(3)
		s = "%s \\%% Basic Agents" % perc
		print(perc, "'%s'"%s)
		newlegend.append(s)

	neworder = np.argsort(newlegend)
	# neworder = neworder[::-1]
	# newlegend = newlegend[::-1]
	# print(results)
	plotMultiWithErrors(name, results, ylim, ylabel="Average Jobs", xlabel=xlabel.replace('#', '\\#'), legend=(newlegend, neworder), order=True)


if __name__ == "__main__":
	# fn = sys.argv[1]
	# print("replotting", fn)
	# fn = "DOL_2020-04-20 13.28.20.341042"
	# codes= ["Jobs Devices", "Devices"]

	# fn = "DOL_2020-04-20 18.13.58.955317"
	# fn = "Max Jobs in Queue_2020-04-24 18.02.21.578890"
	# (name, results, ylim, ylabel, xlabel) = pickle.load(open("{}.pickle".format("/tmp/output/simulator/%s" % fn), "rb"))
	# plotMultiWithErrors(name, results, ylim, ylabel, xlabel, logx=True)
	# replotexp1()
	# replotexp3()
	replotexp4()
	# replotexp5()
