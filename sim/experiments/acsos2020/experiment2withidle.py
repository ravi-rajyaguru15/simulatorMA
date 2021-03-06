
import multiprocessing

import sys
import time
import traceback
from multiprocessing import freeze_support

from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti
from sim.experiments.scenario import REGULAR_SCENARIO_ROUND_ROBIN
from sim.learning.agent.deathwishAgent import deathwishAgent
from sim.learning.agent.lazyDeepAgent import lazyDeepAgent
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.localAgent import localAgent
from sim.learning.agent.minimalDeepAgent import minimalDeepAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.randomAgent import randomAgent
from sim.learning.agent.regretfulTableAgent import regretfulTableAgent
from sim.learning.state.extendedSystemState import extendedSystemState
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.simulations import localConstants, constants
from sim.simulations.SimpleSimulation import SimpleSimulation
import os

from sim.simulations.variable import Constant
from sim.tasks.tasks import HARD, EASY

maxjobs = 20

def runThread(agent, numEpisodes, results, finished):
    # constants.CENTRALISED_LEARNING = False
    exp = SimpleSimulation(numDevices=2, maxJobs=maxjobs, agentClass=agent, tasks=[HARD], systemStateClass=extendedSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, reconsiderBatches=True)
    # exp.scenario.setInterval(1)
    exp.setFpgaIdleSleep(1e-3)
    exp.setBatterySize(1e-1)

    e = None
    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode(e)

            results.put(["Jobs %s" % exp.sharedAgent.__name__, e, exp.numFinishedJobs])
            results.put(["Duration %s" % exp.sharedAgent.__name__, e, exp.getCurrentTime()])
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
    if exp.sharedAgent.__class__ == minimalTableAgent:
        plotting.plotModel(exp.sharedAgent, drawLabels=False)

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
    # agentsToTest = [minimalTableAgent, lazyTableAgent, randomAgent] # , localAgent] # , randomAgent]
    agentsToTest = [minimalTableAgent] # , localAgent] # , randomAgent]
    for agent in agentsToTest: # [minimalAgent, lazyAgent]:
        for _ in range(localConstants.REPEATS):
            processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodes * 2)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    # plotting.plotMulti("experiment2withidle", title="experiment 2 with idle", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    plotting.plotMultiSubplots("experiment2withidle", results=results, ylabel=["Job #", "Duration (in s)"], subplotCodes=["Job", "Duration"], xlabel="Episode #") # , save=True)

if __name__ == "__main__":
    try:
        run(1e2)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")
