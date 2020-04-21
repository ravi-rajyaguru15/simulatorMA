
import multiprocessing

import sys
import time
import traceback
from multiprocessing import freeze_support

from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti
from sim.experiments.scenario import REGULAR_SCENARIO_ROUND_ROBIN
from sim.learning.agent.lazyDeepAgent import lazyDeepAgent
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.localAgent import localAgent
from sim.learning.agent.minimalDeepAgent import minimalDeepAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.randomAgent import randomAgent
from sim.learning.agent.regretfulTableAgent import regretfulTableAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.simulations import localConstants, constants
from sim.simulations.SimpleSimulation import SimpleSimulation
import os

from sim.simulations.variable import Constant
from sim.tasks.tasks import HARD, EASY

maxjobs = 5

def runThread(agent, numEpisodes, results, finished):
    exp = SimpleSimulation(numDevices=2, maxJobs=maxjobs, agentClass=agent, tasks=[EASY], systemStateClass=minimalSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN)
    # exp.scenario.setInterval(1)
    exp.setBatterySize(1e-1)
    exp.setFpgaIdleSleep(0.5)

    e = None
    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode()

            results.put(["%s" % exp.sharedAgent.__name__, e, exp.numFinishedJobs])
    except:
        debug.printCache()
        traceback.print_exc(file=sys.stdout)
        print(agent, e)
        print("Error in experiment ̰:", exp.time)
        sys.exit(0)

    finished.put(True)

    print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)

    # if exp.sharedAgent.__class__ == minimalTableAgent:
    # plotting.plotModel(exp.sharedAgent, drawLabels=True)

def run(numEpisodes):
    print("starting experiment")

    processes = list()
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()

    # localConstants.REPEATS = 10
    numEpisodes = int(numEpisodes)
    agentsToTest = [minimalTableAgent, lazyTableAgent, randomAgent] # , localAgent]
    for agent in agentsToTest: # [minimalAgent, lazyAgent]:
        for _ in range(localConstants.REPEATS):
            processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(agentsToTest) * numEpisodes * localConstants.REPEATS)

    # plotting.plotMultiWithErrors("Number of Jobs", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    plotting.plotMulti("experiment1", title="experiment 1", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)

if __name__ == "__main__":
    try:
        run(2e2)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")