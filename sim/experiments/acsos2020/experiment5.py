import multiprocessing

import sys
import numpy as np

from sim import plotting
from sim.experiments.experiment import setupMultithreading, executeMulti
from sim.experiments.scenario import REGULAR_SCENARIO_ROUND_ROBIN
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.randomAgent import randomAgent
from sim.learning.state.extendedSystemState import extendedSystemState
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.simulations import constants, localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.tasks.tasks import HARD, EASY

numDevices = 10
interval = 1 # 0.1
def threadRun(percentageMinimal, episodeNum, results, finished):
    exp = SimpleSimulation(numDevices=numDevices, maxJobs=50, tasks=[HARD], centralisedLearning=False,  systemStateClass=minimalSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN)
    exp.scenario.setInterval(interval/numDevices)
    exp.setBatterySize(1e-1)
    exp.setFpgaIdleSleep(1e-3)

    numMinimal = int(numDevices * percentageMinimal)
    numRandom = numDevices - numMinimal
    agents = [minimalTableAgent] * numMinimal + [randomAgent] * numRandom

    for agent, device in zip(agents, exp.devices):
        device.agent = agent(reconsiderBatches=False, systemState=exp.currentSystemState, owner=device, offPolicy=exp.offPolicy)
        device.agent.setDevices(exp.devices)
        # print("set agent", agent, agent.__name__, device.agent, device.agent.__name__)

    for e in range(int(episodeNum)):
        exp.simulateEpisode(e)
        totalMinimalAgentJobs = 0
        for i in range(numMinimal):
            dev = exp.devices[i]
            assert dev.agent.__class__ == minimalTableAgent
            totalMinimalAgentJobs += dev.numJobsDone

        results.put(["%d %% Basic Agents" % (int(percentageMinimal * 100.)), e, totalMinimalAgentJobs / numMinimal])

        # sys.stdout.write("\rProgress: %.2f%%" % ((e+1)/episodeNum*100.))

    finished.put(True)


def run(episodeNum):
    episodeNum = int(episodeNum)

    setupMultithreading()
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()

    processes = []
    for _ in range(localConstants.REPEATS):
        for percentage in np.linspace(0.1, 1.0, num=10):
            processes.append(multiprocessing.Process(target=threadRun, args=(percentage, episodeNum, results, finished)))

    results = executeMulti(processes, results, finished, numResults=episodeNum * len(processes))

    # plotting.plotMulti("Competing Agents", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)
    plotting.plotMultiWithErrors("Competing Agents", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)

if __name__ == "__main__":
    localConstants.REPEATS = 8
    run(2e2)
