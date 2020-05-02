import multiprocessing

import sys

from sim import plotting
from sim.experiments.experiment import setupMultithreading, executeMulti
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.simulations import constants, localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.tasks.tasks import HARD, EASY

numDevices = 3
def threadRun(episodeNum, results, finished):
    exp = SimpleSimulation(numDevices=numDevices, maxJobs=100, tasks=[HARD], centralisedLearning=False)
    exp.setBatterySize(1e-1)
    exp.setFpgaIdleSleep(1e-3)

    for agent, device in zip([lazyTableAgent, minimalTableAgent, minimalTableAgent], exp.devices):
        device.agent = agent(reconsiderBatches=False, systemState=exp.currentSystemState, owner=device, offPolicy=exp.offPolicy)
        device.agent.setDevices(exp.devices)
        print("set agent", agent, agent.__name__, device.agent, device.agent.__name__)


    print([device.agent.__name__ for device in exp.devices])
    for e in range(int(episodeNum)):
        exp.simulateEpisode(e)
        for device in exp.devices:
            # print("putting results", device.agent.__name__, device.numJobsDone)
            # results.put(["Agent %s" % device.agent.__name__, e, device.currentTime.current])
            results.put(["Device %d Agent %s" % (device.index, device.agent.__name__), e, device.numJobsDone])

        sys.stdout.write("\rProgress: %.2f%%" % ((e+1)/episodeNum*100.))

    finished.put(True)


def run(episodeNum):
    episodeNum = int(episodeNum)

    setupMultithreading()
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()

    processes = []
    for _ in range(localConstants.REPEATS):
        processes.append(multiprocessing.Process(target=threadRun, args=(episodeNum, results, finished)))

    results = executeMulti(processes, results, finished, numResults=episodeNum * numDevices * len(processes))

    # plotting.plotMulti("Competing Agents", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    plotting.plotMultiWithErrors("Competing Agents", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)

if __name__ == "__main__":
    localConstants.REPEATS = 1
    run(1e2)
