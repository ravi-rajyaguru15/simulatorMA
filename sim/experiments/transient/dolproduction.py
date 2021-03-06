
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

def runThread(agent, numEpisodes, numDevices, taskOptions, interval, results, finished):
    constants.CENTRALISED_LEARNING = False
    exp = SimpleSimulation(numDevices=numDevices, maxJobs=10, agentClass=agent, tasks=taskOptions, systemStateClass=targetedSystemState, reconsiderBatches=False, scenarioTemplate=RANDOM_SCENARIO_ROUND_ROBIN, centralisedLearning=False)
    exp.scenario.setInterval(interval)
    exp.setFpgaIdleSleep(5)
    exp.setBatterySize(1e0)

    e = None
    try:
        #pretrain
        # for e in range(0):
        #     exp.simulateEpisode()

        for e in range(numEpisodes):
            debug.infoEnabled = False
            if e > numEpisodes / 2:
                for dev in exp.devices:
                    dev.agent.setProductionMode(True)
            exp.simulateEpisode()

            dol_ind_task, dol_task_ind = DOL(exp.devices, taskOptions)

            results.put(["DOL Devices %d" % numDevices, e, dol_ind_task])
            results.put(["Jobs Devices %d" % numDevices, e, exp.numFinishedJobs / 1000])
            # results.put(["Interval %.2f" % interval, e, dol_ind_task])


        finished.put("")

    except:
        debug.printCache()
        traceback.print_exc(file=sys.stdout)
        print(agent, e)
        print("Error in experiment????:", exp.time)
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

    # numDevices = 6
    # localConstants.REPEATS = 10
    numEpisodes = int(numEpisodes)
    # agentsToTest = [minimalTableAgent] #, lazyTableAgent]
    # tasks = [[EASY], [EASY, HARD]]
    taskOptions = [EASY, HARD]
    # taskOptions = [HARD, ALTERNATIVE]
    for t in range(len(taskOptions)):
        taskOptions[t].identifier = t
        print("task", taskOptions[t], taskOptions[t].identifier)

    # testIntervals = np.logspace(-4, 0, num=5)

    # testIntervals = [1e0]

    # for agent in agentsToTest: # [minimalAgent, lazyAgent]:
    localConstants.REPEATS = 1
    for _ in range(localConstants.REPEATS):
        # for taskOptions in tasks:
        # for interval in testIntervals:
        # interval = testIntervals
        for numDevices in [2, 12]:
            processes.append(multiprocessing.Process(target=runThread, args=(regretfulTableAgent, numEpisodes, numDevices, taskOptions, 1, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodes * 2) #, assembly=experiment.assembleResultsBasic)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    localConstants.SAVE_GRAPH = True
    plotting.plotMultiWithErrors("DOL", results=results, ylabel="DOL", xlabel="Episode #")


if __name__ == "__main__":
    setupMultithreading()
    try:
        run(1e2)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")