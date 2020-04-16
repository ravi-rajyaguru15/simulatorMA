
import multiprocessing

import sys
import time
import traceback
from multiprocessing import freeze_support

from sim import debug, counters, plotting
from sim.experiments import experiment
from sim.experiments.experiment import executeMulti, setupMultithreading, assembleResultsBasic
from sim.experiments.scenario import RANDOM_SCENARIO_RANDOM, RANDOM_SCENARIO_ALL, RANDOM_SCENARIO_ROUND_ROBIN
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.regretfulTableAgent import regretfulTableAgent
from sim.learning.state.extendedSystemState import extendedSystemState
from sim.learning.state.targetedSystemState import targetedSystemState
from sim.simulations import localConstants, constants
from sim.simulations.SimpleSimulation import SimpleSimulation
import os

from sim.simulations.variable import Constant
from sim.tasks.tasks import EASY, HARD, ALTERNATIVE


def runThread(agent, numEpisodes, numDevices, taskOptions, results, finished):
    exp = SimpleSimulation(numDevices=numDevices, maxJobs=10, agentClass=agent, tasks=taskOptions, systemStateClass=targetedSystemState, reconsiderBatches=False, scenarioTemplate=RANDOM_SCENARIO_ROUND_ROBIN, centralisedLearning=False)
    exp.scenario.setInterval(1)
    exp.setFpgaIdleSleep(60)
    exp.setBatterySize(1e0)

    e = None
    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode()


            for device in exp.devices:
                for action in device.agent.possibleActions:
                    results.put(["Device %d %s" % (device.index, action), e, device.agent.getChosenAction(action)])
            #     for task in taskOptions:
            #         results.put(["Device %d Task %d" % (device.index, task.identifier), e, device.getNumTasksDone(task)])
                    # print(e, "Device %d Task %s" % (device.index, task), e, device.getNumTasksDone(task))
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

    # print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)

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

    numDevices = 2
    # localConstants.REPEATS = 10
    numEpisodes = int(numEpisodes)
    # agentsToTest = [minimalTableAgent] #, lazyTableAgent]
    # tasks = [[EASY], [EASY, HARD]]
    taskOptions = [EASY, HARD]
    # taskOptions = [HARD, ALTERNATIVE]
    for t in range(len(taskOptions)):
        taskOptions[t].identifier = t
        print("task", taskOptions[t], taskOptions[t].identifier)

    # for agent in agentsToTest: # [minimalAgent, lazyAgent]:
    for _ in range(localConstants.REPEATS):
        # for taskOptions in tasks:
        processes.append(multiprocessing.Process(target=runThread, args=(regretfulTableAgent, numEpisodes, numDevices, taskOptions, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodes * 3 * numDevices, assembly=experiment.assembleResultsBasic)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    plotting.plotMulti("Number of times action chosen", results=results, ylabel="Action Count", xlabel="Episode #")  # , save=True)


if __name__ == "__main__":
    setupMultithreading()
    try:
        run(1e4)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")