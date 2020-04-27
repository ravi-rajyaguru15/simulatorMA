
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
    exp = SimpleSimulation(numDevices=numDevices, maxJobs=50, agentClass=agent, tasks=taskOptions, systemStateClass=targetedSystemState, reconsiderBatches=False, scenarioTemplate=RANDOM_SCENARIO_ROUND_ROBIN, centralisedLearning=False)
    norminterval = float(interval) / numDevices

    print("scaling interval from", interval, "to", norminterval)
    exp.scenario.setInterval(norminterval)
    exp.setFpgaIdleSleep(1e-3)
    exp.setBatterySize(1e-1)

    assert numEpisodes % 2 == 0

    offset = 0
    e = 0
    reduced = False
    try:
        for i in range(2):
            for e in range(int(numEpisodes / 2)):
                exp.simulateEpisode(e)
                dol_ind_task, dol_task_ind = DOL(exp.devices, taskOptions)
                results.put(["DOL %d devices" % numDevices, offset + e, dol_ind_task])
                results.put(["Jobs Completed %d devices" % numDevices, offset + e, exp.numFinishedJobs])
                # results.put(["Interval %.2f" % interval, e, dol_ind_task])

            if not reduced:
                print()
                # remove half
                for i in range(int(numDevices / 2)):
                    exp.removeDevice()
                reduced = True
                oldinterval = norminterval
                norminterval = float(interval) / len(exp.devices)
                print("scaling reduced interval from", oldinterval, "to", norminterval, "(%d to %d)" % (numDevices, len(exp.devices)))

                print("reduce to", exp.devices)
                offset = e + 1

        finished.put("")

    except:
        debug.printCache()
        traceback.print_exc(file=sys.stdout)
        print(agent, e)
        print("Error in experiment ̰:", exp.time)
        print(agent, numEpisodes, numDevices, taskOptions, interval, e, offset, reduced)
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

    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()

    numEpisodes = int(numEpisodes)
    taskOptions = [EASY, HARD]
    for t in range(len(taskOptions)):
        taskOptions[t].identifier = t
        print("task", taskOptions[t], taskOptions[t].identifier)

    # localConstants.REPEATS = 128
    localConstants.REPEATS = 16
    for _ in range(localConstants.REPEATS):
        for numDevices in [4, 8, 12]: #, 6, 8, 10, 12]:
        # for numDevices in [4, 12]:
            processes.append(multiprocessing.Process(target=runThread, args=(minimalTableAgent, numEpisodes, numDevices, taskOptions, 1, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodes * 2) #, assembly=experiment.assembleResultsBasic)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    # plotting.plotMultiWithErrors("DOL", results=results, ylabel="DOL", xlabel="Episode #")


    codes = ["Jobs Completed", "DOL"]
    plotting.plotMultiSubplots("experiment4normalised", results=results, ylabel=["System Jobs #", "DOL"], xlabel="Episode #", subplotCodes=codes, plotErrors=True)


if __name__ == "__main__":
    setupMultithreading()
    try:
        run(1e3)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")