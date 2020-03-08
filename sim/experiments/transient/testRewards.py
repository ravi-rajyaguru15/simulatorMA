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
from sim.simulations import simulationResults, localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation

# sim.simulations.constants.NUM_DEVICES = 1


def runThread(agent, numEpisodes, results, finished, histories):
    exp = SimpleSimulation(numDevices=1, maxJobs=3, agentClass=agent)
    exp.setFpgaIdleSleep(5)
    exp.setBatterySize(1e0)

    # sim.simulations.constants.FPGA_IDLE_SLEEP = 5
    # sim.simulations.constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
    # sim.simulations.constants.TOTAL_TIME = 1e3
    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode()

            results.put(["Episode reward %s" % exp.sharedAgent, e, exp.sharedAgent.episodeReward])
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
    print("starting experiment")
    debug.enabled = False
    debug.learnEnabled = False
    debug.infoEnabled = False



    processes = list()
    # sim.simulations.constants.MINIMUM_BATCH = 1e7

    # offloadingOptions = [True, False]
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()
    histories = multiprocessing.Queue()
    # sim.simulations.constants.REPEATS = 1

    # for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
    # 	for roundRobin in np.arange(1e0, 1e1, 2.5):
    numEpisodes = int(1e4)
    agentsToTest = [lazyAgent] #     agentsToTest = [lazyAgent] #
    for agent in agentsToTest: # [minimalAgent, lazyAgent]:
        for _ in range(localConstants.REPEATS):
            processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished, histories)))

    results = executeMulti(processes, results, finished, numResults=len(agentsToTest) * numEpisodes * localConstants.REPEATS)

    plotting.plotMultiWithErrors("Episode Rewards", results=results, ylabel="Reward", xlabel="Episode #")  # , save=True)
    # plotting.plotAgentHistory(histories.get())


if __name__ == "__main__":
    freeze_support()
    try:
        run()
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")