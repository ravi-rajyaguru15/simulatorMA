
import multiprocessing

import sys
import time
import traceback
from multiprocessing import freeze_support

from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti
from sim.learning.agent.lazyDeepAgent import lazyDeepAgent
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalDeepAgent import minimalDeepAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.simulations import localConstants, constants
from sim.simulations.SimpleSimulation import SimpleSimulation
import os

from sim.simulations.variable import Constant
from sim.tasks.tasks import HARD


def runThread(agent, numEpisodes, results, finished):
    constants.CENTRALISED_LEARNING = False
    exp = SimpleSimulation(numDevices=2, maxJobs=100, agentClass=agent, tasks=[HARD])
    exp.scenario.setInterval(1)
    exp.setBatterySize(1e-1)

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
    print("starting experiment")

    processes = list()
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()

    numEpisodes = int(numEpisodes)
    agentsToTest = [minimalDeepAgent, minimalTableAgent, lazyDeepAgent, lazyTableAgent] # ,  , localAgent] # , randomAgent]
    for agent in agentsToTest: # [minimalAgent, lazyAgent]:
        for _ in range(localConstants.REPEATS):
            processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(agentsToTest) * numEpisodes * localConstants.REPEATS)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    plotting.plotMulti("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)


if __name__ == "__main__":
    try:
        run(1e4)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")