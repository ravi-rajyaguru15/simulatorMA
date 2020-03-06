
import multiprocessing

import sys
import time
import traceback
from multiprocessing import freeze_support

from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
import os

from sim.simulations.variable import Constant



def runThread(agent, numEpisodes, results, finished):
    exp = SimpleSimulation(numDevices=2, maxJobs=6, agentClass=agent)

    exp.setFpgaIdleSleep(5)
    exp.setBatterySize(1e0)

    e = None
    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode()

            results.put(["Agent %s" % agent.__name__, e, exp.numFinishedJobs])
    except:
        debug.printCache()
        traceback.print_exc(file=sys.stdout)
        print(agent, e)
        print("Error in experiment ̰:", exp.time)
        sys.exit(0)

    finished.put(True)
    # assert simulationResults.learningHistory is not None
    # histories.put(simulationResults.learningHistory)
    # print("\nsaving history", simulationResults.learningHistory, '\nr')

    print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)

    # exp.sharedAgent.printModel()


def run(numEpisodes):
    multiprocessing.set_start_method('spawn')
    print("starting experiment")
    debug.enabled = False
    debug.learnEnabled = False
    debug.infoEnabled = False


    processes = list()
    # sim.simulations.constants.MINIMUM_BATCH = 1e7

    # offloadingOptions = [True, False]
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()
    # experiments = multiprocessing.Queue()
    # REPEATS = 1

    # localConstants.REPEATS = 10
    numEpisodes = int(numEpisodes)
    agentsToTest = [minimalAgent, lazyAgent]
    for agent in agentsToTest: # [minimalAgent, lazyAgent]:
        for _ in range(localConstants.REPEATS):
            processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(agentsToTest) * numEpisodes * localConstants.REPEATS)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    plotting.plotMulti("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)


if __name__ == "__main__":
    try:
        run(1e2)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")