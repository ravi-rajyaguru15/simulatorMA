import multiprocessing

import sys
import traceback
from multiprocessing import freeze_support
import numpy as np

import sim
from sim import debug, counters, plotting
from sim.devices.components.powerPolicy import IDLE_TIMEOUT
from sim.experiments.experiment import executeMulti
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.offloading.offloadingPolicy import REINFORCEMENT_LEARNING
from sim.simulations import simulationResults
from sim.simulations.SimpleSimulation import SimpleSimulation

sim.simulations.constants.NUM_DEVICES = 2


def runThread(agent, numEpisodes, results, finished, histories):
    print("before")
    exp = SimpleSimulation(agentClass=agent)
    print("after")

    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode()

            results.put(["Agent %s" % agent, e, exp.numFinishedJobs])
    except:
        traceback.print_exc(file=sys.stdout)
        print(agent, e)
        print("Error in experiment ̰:", exp.time)
        debug.printCache(200)
        sys.exit(0)

    finished.put(True)
    # assert simulationResults.learningHistory is not None
    # histories.put(simulationResults.learningHistory)
    # print("\nsaving history", simulationResults.learningHistory, '\nr')

    print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)

    exp.sharedAgent.printModel()


def run():
    print("starting experiment")
    debug.enabled = False
    debug.learnEnabled = False
    debug.infoEnabled = False

    sim.simulations.constants.FPGA_IDLE_SLEEP = 5
    sim.simulations.constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
    # sim.simulations.constants.TOTAL_TIME = 1e3
    sim.simulations.constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e0
    sim.simulations.constants.MAX_JOBS = 6

    processes = list()
    sim.simulations.constants.MINIMUM_BATCH = 1e7

    # offloadingOptions = [True, False]
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()
    histories = multiprocessing.Queue()
    sim.simulations.constants.REPEATS = 1

    numEpisodes = int(5e1)
    agentsToTest = [minimalAgent, lazyAgent]
    for agent in agentsToTest: # [minimalAgent, lazyAgent]:
        for _ in range(sim.simulations.constants.REPEATS):
            processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished, histories)))

    results = executeMulti(processes, results, finished, numResults=len(agentsToTest) * numEpisodes * sim.simulations.constants.REPEATS)

    plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)


if __name__ == "__main__":
    freeze_support()
    try:
        run()
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")