import sim
from sim.simulations import localConstants

cache = []
currentCache = 0
outputFile = None


class settings:
    maxCache = 1000
    default = 37
    enabled = False
    learnEnabled = False
    infoEnabled = False
    # fileOutput = False


# print to console in a fancy colour
# options are k r g y b p c w
def out(string, colour=None):
    _push(string, colour, settings.enabled)


def infoOut(string="", colour=None):
    _push(string, colour, settings.infoEnabled)


def learnOut(string="", colour=None):
    _push(string, colour, settings.learnEnabled)


def _push(string, colour, printImmediate=True):
    if not printImmediate:
        if localConstants.DEBUG_FILE:
            if sim.debug.outputFile is None:
                print("opening log file", localConstants.OUTPUT_DIRECTORY + "debug.log")
                sim.debug.outputFile = open(localConstants.OUTPUT_DIRECTORY + "debug.log", 'w')
            sim.debug.outputFile.write(str(string) + '\n')
        elif localConstants.DEBUG_HISTORY:
            sim.debug.cache.append((string, colour))
            sim.debug.currentCache += 1
            if sim.debug.currentCache > settings.maxCache:
                sim.debug.cache = sim.debug.cache[-settings.maxCache:]
                sim.debug.currentCache = settings.maxCache
    else:
        _print(string, colour)


def _print(string, colour):
    if colour is None:
        print(string)

    else:
        if colour == 'k':
            code = 30
        elif colour == 'r':
            code = 31
        elif colour == 'g':
            code = 32
        elif colour == 'y':
            code = 33
        elif colour == 'b':
            code = 34
        elif colour == 'p':
            code = 35
        elif colour == 'c':
            code = 36
        elif colour == 'w':
            code = 37
        elif colour == 'dg':
            code = 92
        else:
            raise Exception("Colour {0} not recognised".format(colour))

        print("\033[{0}m{1}\033[{2}m".format(code, string, settings.default))


def printCache(numLines=None):
    print("debug log:")
    if numLines is None: numLines = 0
    entry = ""
    try:
        for entry in cache[-numLines:]:
            _print(entry[0], entry[1])
    except:
        print("Error in Debug queue:", entry)