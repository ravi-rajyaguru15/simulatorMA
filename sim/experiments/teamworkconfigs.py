
import multiprocessing

import sys
import time
import traceback
from math import inf
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
        for e in range(0):
            exp.simulateEpisode()

        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode()

            times = np.zeros((len(taskOptions),))
            percentages = np.zeros((numDevices,))
            for device in exp.devices:
                for t in range(len(taskOptions)):
                    task = taskOptions[t]
                    times[t] = device.fpga.getConfigTime(task)
                sum = np.sum(times)
                if sum > 0:
                    perc = times[0] / sum
                else:
                    perc = 0.5
                if perc < 0.5: perc = 1. - perc
                percentages[device.index] = perc

            # results.put(["", np.average(percentages), exp.numFinishedJobs])
            results.put(["Interval %.2f" % interval, np.average(percentages), exp.numFinishedJobs])
        # for device in exp.devices:
        #     device.agent.setProductionMode()
        # exp.simulateEpisode()


        finished.put("")
                # if times[1] == 0:
                #     ratio = inf
                # else:
                #     ratio = times[0] / times[1]
                # if ratio < 1 and ratio != 0: ratio = 1. / ratio
                # results.put(["Device %d EASY/HARD" % (device.index), e, ratio])
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

    testIntervals = np.logspace(-2, 1, num=4)
    # testIntervals = [1e-1]

    # for agent in agentsToTest: # [minimalAgent, lazyAgent]:
    localConstants.REPEATS = 25
    for _ in range(localConstants.REPEATS):
        # for taskOptions in tasks:
        for interval in testIntervals:
            # print(interval)
            processes.append(multiprocessing.Process(target=runThread, args=(minimalTableAgent, numEpisodes, numDevices, taskOptions, interval, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodes, assembly=experiment.assembleResultsBasic)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    plotting.plotMulti("Number of Jobs", results=results, ylabel="Total Jobs", xlabel="Favoritism")  # , save=True)


if __name__ == "__main__":
    setupMultithreading()
    try:
        run(1e1)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")