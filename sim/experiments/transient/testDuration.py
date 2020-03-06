import multiprocessing

import sys
import traceback
from multiprocessing import freeze_support

import sim
from sim import debug, counters, plotting
from sim.devices.components.powerPolicy import IDLE_TIMEOUT
from sim.experiments.experiment import executeMulti, assembleResultsBasic
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.offloading.offloadingPolicy import REINFORCEMENT_LEARNING
from sim.simulations import simulationResults
from sim.simulations.SimpleSimulation import SimpleSimulation

def runThread(agent, numEpisodes, results, finished, histories):
    exp = SimpleSimulation(numDevices=2, maxJobs=6, agentClass=agent)
    exp.setFpgaIdleSleep(5)
    exp.setBatterySize(1e0)

    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode()
            results.put(["Duration %s" % exp.sharedAgent, e, exp.getCurrentTime()])
            # results.put(["Episode reward %s" % exp.sharedAgent, e, exp.sharedAgent.episodeReward])
    except:
        debug.printCache(200)
        traceback.print_exc(file=sys.stdout)
        print(agent, e)
        print("Error in experiment ̰:", exp.time)
        sys.exit(0)

    finished.put(True)
    assert simulationResults.learningHistory is not None
    histories.put(simulationResults.learningHistory)
    print("\nsaving history", simulationResults.learningHistory, '\nr')

    print("forward", counters.NUM_FORWARD, "backward", counters.NUM_BACKWARD)

    exp.sharedAgent.printModel()

def run():
    multiprocessing.set_start_method('spawn')
    print("starting experiment")
    debug.enabled = False
    debug.learnEnabled = False
    debug.infoEnabled = False
    # debug.fileOutput = True

    processes = list()

    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()
    histories = multiprocessing.Queue()
    REPEATS = 1

    numEpisodes = int(1e2)
    agentsToTest = [minimalAgent, lazyAgent]
    for agent in agentsToTest: # [minimalAgent, lazyAgent]:
        for _ in range(REPEATS):
            processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished, histories)))

    results = executeMulti(processes, results, finished, numResults=len(agentsToTest) * numEpisodes * REPEATS)

    plotting.plotMultiWithErrors("Episode duration", results=results, ylabel="Duration", xlabel="Episode #")  # , save=True)

if __name__ == "__main__":
    freeze_support()
    try:
        run()
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")