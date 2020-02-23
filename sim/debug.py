import sim

default = 37
enabled = False
learnEnabled = False
infoEnabled = False

cache = []
maxCache = 1000


# print to console in a fancy colour
# options are k r g y b p c w
def out(string, colour=None, enable=None):
    _push(string, colour, enabled)


def infoOut(string="", colour=None):
    _push(string, colour, infoEnabled)


def learnOut(string="", colour=None):
    _push(string, colour, learnEnabled)


def _push(string, colour, printImmediate=True):
    if not printImmediate:
        sim.debug.cache.append((string, colour))
        if len(sim.debug.cache) > maxCache:
            sim.debug.cache = sim.debug.cache[-maxCache:]
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

        print("\033[{0}m{1}\033[{2}m".format(code, string, default))


def printCache(numLines=None):
    print("debug log:")
    if numLines is None: numLines = 0
    for entry in cache[-numLines:]:
        _print(entry[0], entry[1])