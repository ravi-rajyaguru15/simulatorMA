
import multiprocessing

import sys
import time
import traceback
from multiprocessing import freeze_support

from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti, setupMultithreading
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
import os

from sim.simulations.variable import Constant
from sim.tasks.tasks import EASY, HARD


def runThread(agent, numEpisodes, taskOptions, results, finished):
    exp = SimpleSimulation(numDevices=4, maxJobs=6, agentClass=agent, tasks=taskOptions)
    exp.scenario.setInterval(1)
    exp.setFpgaIdleSleep(5)
    exp.setBatterySize(1e0)

    e = None
    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode()

            results.put(["Agent %s (%s)" % (agent.__name__, len(taskOptions)), e, exp.numFinishedJobs])
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
    print("starting experiment")

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
            for taskOptions in [[EASY], [EASY, HARD]]:
                print(taskOptions)
                processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, taskOptions, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodes)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    plotting.plotMulti("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)


if __name__ == "__main__":
    setupMultithreading()
    try:
        run(1e3)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")