
import multiprocessing

import sys
import time
import traceback
from multiprocessing import freeze_support

from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti
from sim.learning.agent.randomAgent import randomAgent
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
import os

from sim.simulations.variable import Constant
from sim.tasks.tasks import HARD


def runThread(agent, numEpisodes, results, finished):
    exp = SimpleSimulation(numDevices=16, maxJobs=25, agentClass=agent, tasks=[HARD])
    exp.scenario.setInterval(1)
    exp.setBatterySize(1e-1)

    e = None
    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode()

            try:
                averageLifetime = exp.totalFinishedJobsLifetime / exp.numFinishedJobs
            except ZeroDivisionError:
                print("no jobs done!")
                print(agent, numEpisodes, e)
                averageLifetime = 0
            results.put(["Agent %s" % agent.__name__, e, averageLifetime])
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
    agentsToTest = [minimalAgent, lazyAgent, randomAgent] # localAgent]
    for agent in agentsToTest: # [minimalAgent, lazyAgent]:
        for _ in range(localConstants.REPEATS):
            processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(agentsToTest) * numEpisodes * localConstants.REPEATS)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    plotting.plotMulti("Episode Duration", results=results, ylabel="Average Job lifetime (in s)", xlabel="Episode #")  # , save=True)


if __name__ == "__main__":
    try:
        run(1e3)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")