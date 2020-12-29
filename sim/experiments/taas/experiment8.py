
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
from sim.learning.agent.regretfulDeepAgent import regretfulDeepAgent
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
    constants.OFF_POLICY = True
    exp = SimpleSimulation(numDevices=numDevices, maxJobs=50, agentClass=agent, tasks=taskOptions, systemStateClass=targetedSystemState, reconsiderBatches=False, scenarioTemplate=RANDOM_SCENARIO_ROUND_ROBIN, centralisedLearning=False)
    exp.scenario.setInterval(interval)
    exp.setFpgaIdleSleep(1e-3)
    exp.setBatterySize(1e-1)

    assert numEpisodes % 2 == 0

    offset = 0
    e = 0
    reduced = False
    try:
        debug.infoEnabled = False
        for i in range(2):
            for e in range(int(numEpisodes / 2)):
                exp.simulateEpisode(e)
                dol_ind_task, dol_task_ind = DOL(exp.devices, taskOptions)
                
                results.put(["DOL %d devices" % numDevices, offset + e, dol_ind_task * 100.])
                results.put(["Jobs Completed %d devices" % numDevices, offset + e, exp.numFinishedJobs])
                # results.put(["Interval %.2f" % interval, e, dol_ind_task])

            if not reduced:
                print()
                # remove half
                for i in range(int(numDevices / 2)):
                    exp.removeDevice()
                reduced = True
                print("reduce to", exp.devices)
                offset = e

        finished.put("")

    except:
        debug.printCache()
        traceback.print_exc(file=sys.stdout)
        print(agent, e)
        print("Error in experiment ̰:", exp.time)
        print(agent, numEpisodes, numDevices, taskOptions, interval, e, offset, reduced)
        sys.exit(0)

    finished.put(True)

def run(numEpisodes):
    print("starting experiment")

    processes = list()

    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()

    localConstants.REPEATS = 4

    numEpisodes = int(numEpisodes)
    taskOptions = [EASY, HARD]
    for t in range(len(taskOptions)):
        taskOptions[t].identifier = t
        print("task", taskOptions[t], taskOptions[t].identifier)

    for _ in range(localConstants.REPEATS):
        # for taskOptions in tasks:
        # for interval in testIntervals:
        for numDevices in [4, 8, 12]: #, 6, 8, 10, 12]:
            processes.append(multiprocessing.Process(target=runThread, args=(regretfulDeepAgent, numEpisodes, numDevices, taskOptions, 1, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodes * 2)

    plotting.plotMultiWithErrors("experiment8", results=results, ylabel="DOL", xlabel="Episode #", logy=False)


if __name__ == "__main__":
    setupMultithreading()
    try:
        run(2e1)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")