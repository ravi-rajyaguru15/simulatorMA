import matplotlib as mpl
import matplotlib.pyplot as pp
import numpy as np

colours = ['b', 'r']

def plotWithErrors(x, y=None, errors=None, results=None):
    if y is None:
        y = [result[0] for result in results]
        errors = [result[1] for result in results]

    pp.errorbar(x, y, yerr=errors)
    pp.show()

    
def plotMultiWithErrors(x, results=None, legend=None, ylim=None):
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

    if ylim is not None:
        pp.ylim(ylim)

    pp.show()

    