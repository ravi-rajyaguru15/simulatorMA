default = 37
enabled = True

# print to console in a fancy colour
# options are k r g y b p c w
def out(string, colour=None):
    if not enabled:
        return
    
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
