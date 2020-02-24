import multiprocessing
import sys
import traceback

import sim
from sim import debug, counters, plotting
from sim.devices.components.powerPolicy import IDLE_TIMEOUT
from sim.experiments.experiment import executeMulti
from sim.learning.agent.lazyAgent import lazyAgent
from sim.learning.agent.minimalAgent import minimalAgent
from sim.offloading.offloadingPolicy import REINFORCEMENT_LEARNING
from sim.simulations import constants, simulationResults
from sim.simulations.SimpleSimulation import SimpleSimulation

constants.NUM_DEVICES = 2


def runThread(agent, numEpisodes, results, finished, histories):
    exp = SimpleSimulation(agentClass=agent)

    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode()
            # exp.reset()
            # exp.simulateTime(10)
            # debug.infoEnabled = True
            # while not exp.finished:
            #     exp.simulateTick()
            results.put(["Duration %s" % agent, e, exp.getCurrentTime()])
            results.put(["Episode reward %s" % agent, e, exp.sharedAgent.episodeReward])

            # print("finished:")
            # print(len(exp.finishedJobsList))
            # print("unfinished:")
            # print(exp.unfinishedJobsList)
            # results.put(["Overall reward", e, exp.sharedAgent.totalReward])
            # print(exp.getCurrentTime(), exp.sharedAgent.episodeReward, exp.sharedAgent.totalReward)
    except:
        traceback.print_exc(file=sys.stdout)
        print(agent, e)
        print("Error in experiment ̰:", exp.time)
        debug.printCache(200)
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

    constants.DRAW = False
    constants.FPGA_POWER_PLAN = IDLE_TIMEOUT
    constants.FPGA_IDLE_SLEEP = 5
    constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
    # constants.TOTAL_TIME = 1e3
    constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e0
    constants.MAX_JOBS = 5

    processes = list()
    constants.MINIMUM_BATCH = 1e7

    # offloadingOptions = [True, False]
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()
    histories = multiprocessing.Queue()
    constants.REPEATS = 1

    # for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
    # 	for roundRobin in np.arange(1e0, 1e1, 2.5):
    numEpisodes = int(1e1)
    agentsToTest = [minimalAgent] # , lazyAgent]
    for agent in agentsToTest: # [minimalAgent, lazyAgent]:
        for _ in range(constants.REPEATS):
            processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished, histories)))

    results = executeMulti(processes, results, finished, numResults=len(agentsToTest) * numEpisodes * constants.REPEATS * 2)

    plotting.plotMultiWithErrors("Episode duration", results=results, ylabel="Reward", xlabel="Episode #")  # , save=True)
    # plotting.plotAgentHistory(histories.get())


if __name__ == "__main__":
    try:
        run()
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")