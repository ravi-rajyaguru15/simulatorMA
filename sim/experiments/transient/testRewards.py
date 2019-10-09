import sim.constants
import sim.variable
import sim.debug
from sim.simulation import simulation
import sim.plotting
import sim.experiments.experiment
import sim.offloadingDecision
import sim.job
import sim.counters
import sim.results
import sim.powerPolicy
import sim.offloadingPolicy

import multiprocessing
import sys
import traceback

sim.constants.NUM_DEVICES = 1


def runThread(numEpisodes, results, finished, histories):
    exp = simulation(hardwareAccelerated=True)
    sim.simulation.current = exp

    try:
        for e in range(numEpisodes):
            exp.simulateEpisode()
            results.put(["Duration", e, exp.time.current])
            results.put(["Episode reward", e, sim.offloadingDecision.sharedAgent.episodeReward])
            results.put(["Overall reward", e, sim.offloadingDecision.sharedAgent.totalReward])
    except:
        traceback.print_exc(file=sys.stdout)
        print("Error in experiment ̰:", exp.time)
        sys.exit(0)

    finished.put(True)
    histories.put(sim.results.learningHistory)
    assert sim.results.learningHistory is not None
    # print("\nsaving history", sim.results.learningHistory, '\nr')

    print("forward", sim.counters.NUM_FORWARD, "backward", sim.counters.NUM_BACKWARD)


def run():
    print("starting experiment")
    sim.debug.enabled = False
    sim.debug.learnEnabled = False
    sim.debug.infoEnabled = True

    sim.constants.DRAW = False
    sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IDLE_TIMEOUT
    sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.REINFORCEMENT_LEARNING
    # sim.constants.TOTAL_TIME = 1e3
    sim.constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 5e-2

    processes = list()
    sim.constants.MINIMUM_BATCH = 1e5

    # offloadingOptions = [True, False]
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()
    histories = multiprocessing.Queue()
    sim.constants.REPEATS = 1

    # for jobLikelihood in np.arange(1e-3, 1e-2, 1e-3):
    # 	for roundRobin in np.arange(1e0, 1e1, 2.5):
    numEpisodes = int(2e0)
    for _ in range(sim.constants.REPEATS):
        processes.append(multiprocessing.Process(target=runThread, args=(numEpisodes, results, finished, histories)))

    results = sim.experiments.experiment.executeMulti(processes, results, finished,
                                                      numResults=numEpisodes * sim.constants.REPEATS * 3)

    # sim.plotting.plotMultiWithErrors("Episode duration", results=results, ylabel="Reward", xlabel="Episode #")  # , save=True)
    # sim.plotting.plotAgentHistory(histories.get())


if __name__ == "__main__":
    try:
        run()
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")