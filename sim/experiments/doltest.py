
import multiprocessing

import sys
import time
import traceback
from math import inf
from multiprocessing import freeze_support

from sim import debug, counters, plotting
from sim.dol import DOL
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
import numpy as np

def runThread(numEpisodesTrain, numEpisodesTest, numDevices, taskOptions, interval, results, finished):
    constants.CENTRALISED_LEARNING = False
    numDevices = int(numDevices)
    exp = SimpleSimulation(numDevices=numDevices, maxJobs=10, agentClass=regretfulTableAgent, tasks=taskOptions, systemStateClass=targetedSystemState, reconsiderBatches=False, scenarioTemplate=RANDOM_SCENARIO_ROUND_ROBIN, centralisedLearning=False)
    exp.scenario.setInterval(interval)
    exp.setFpgaIdleSleep(5)
    exp.setBatterySize(1e0)

    e = None
    try:
        #pretrain
        # for e in range(0):
        #     exp.simulateEpisode()

        debug.infoEnabled = False
        for e in range(numEpisodesTrain):
            exp.simulateEpisode()

        # dols = list()
        for e in range(numEpisodesTest):
            exp.simulateEpisode()

            dol_ind_task, dol_task_ind = DOL(exp.devices, taskOptions, addIdle=False)
            results.put(["Devices: %d" % numDevices, interval, dol_ind_task])
            results.put(["Jobs Devices %d" % numDevices, e, exp.numFinishedJobs / 1000])
            # dols.append(dol_ind_task)

        # results.put(["Devices: %d" % numDevices, interval, np.average(dols)])


        finished.put("")

    except:
        debug.printCache()
        traceback.print_exc(file=sys.stdout)
        # print(agent, e)
        print("Error in experiment ̰:", exp.time)
        sys.exit(0)

    finished.put(True)
    # assert simulationResults.learningHistory is not None
    # histories.put(simulationResults.learningHistory)
    # print("\nsaving history", simulationResults.learningHistory, '\nr')

    # print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)

    # exp.sharedAgent.printModel()


def run(numEpisodesTrain, numEpisodesTest):
    print("starting experiment")

    processes = list()
    # sim.simulations.constants.MINIMUM_BATCH = 1e7

    # offloadingOptions = [True, False]
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()
    # experiments = multiprocessing.Queue()
    # REPEATS = 1

    maxDevices = 12
    minDevices = 2
    numDevices = np.linspace(start=minDevices, stop=maxDevices, num=int((maxDevices - minDevices) / 2))
    # localConstants.REPEATS = 10
    numEpisodesTrain, numEpisodesTest = int(numEpisodesTrain), int(numEpisodesTest)
    # agentsToTest = [minimalTableAgent] #, lazyTableAgent]
    # tasks = [[EASY], [EASY, HARD]]
    taskOptions = [EASY, HARD]
    # taskOptions = [HARD, ALTERNATIVE]
    for t in range(len(taskOptions)):
        taskOptions[t].identifier = t
        print("task", taskOptions[t], taskOptions[t].identifier)

    # testIntervals = np.logspace(-4, 0, num=5)
    testIntervals = np.linspace(1e-2, 1, num=3)

    for _ in range(localConstants.REPEATS):
        for interval in testIntervals:
            for devs in numDevices:
                processes.append(multiprocessing.Process(target=runThread, args=(numEpisodesTrain, numEpisodesTest, devs, taskOptions, interval, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodesTest*2) #, assembly=experiment.assembleResultsBasic)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    localConstants.SAVE_GRAPH = True
    plotting.plotMultiWithErrors("DOL", results=results, ylabel="DOL", xlabel="Interval")


if __name__ == "__main__":
    setupMultithreading()
    try:
        run(1e2, 1e2)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")