
import multiprocessing

import sys
import traceback


from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti
from sim.experiments.scenario import REGULAR_SCENARIO_ROUND_ROBIN
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.dqnAgent import dqnAgent
from sim.learning.agent.randomAgent import randomAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.simulations import localConstants, constants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.experiments.experiment import executeMulti, setupMultithreading

from sim.tasks.tasks import HARD
maxjobs = 15
numEnergyStates = 10

def runThread(agent, numEpisodes, results, finished):
    exp = SimpleSimulation(numDevices=2, maxJobs=maxjobs, agentClass=agent, tasks=[HARD], systemStateClass=minimalSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=True, numEnergyLevels=numEnergyStates, trainClassification=False)
    # exp.scenario.setInterval(1)
    exp.sharedAgent.loadModel()
    exp.sharedAgent.setProductionMode()
    exp.setBatterySize(1e-1)
    exp.setFpgaIdleSleep(1e-3)

    e = None
    try:
        for e in range(numEpisodes):
            debug.infoEnabled = False
            exp.simulateEpisode(e)

            agentName = exp.devices[0].agent.__name__
            result = [f"{agentName}", e, exp.numFinishedJobs]
            print(result)
            results.put(result)
            # results.put([f"{agentName}", e, exp.getCurrentTime()])
    except:
        debug.printCache()
        traceback.print_exc(file=sys.stdout)
        print(agent, e)
        print("Error in experiment :", exp.time)
        sys.exit(0)

    finished.put(True)


def run(numEpisodes):
    print("starting experiment")

    processes = list()
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()

    localConstants.REPEATS = 4
    # localConstants.REPEATS = 8
    numEpisodes = int(numEpisodes)
    # agentsToTest = [minimalTableAgent]
    agentsToTest = [dqnAgent] # minimalTableAgent, , localAgent]
    for agent in agentsToTest: # [minimalAgent, lazyAgent]:
        for _ in range(localConstants.REPEATS):
            for centralised in [True]:
                if not (not centralised and agent is randomAgent):
                    processes.append(multiprocessing.Process(target=runThread, args=(agent, numEpisodes, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(processes) * numEpisodes)

    # plotting.plotMultiWithErrors("experiment1", title="experiment 1", results=results, ylabel="", xlabel="Episode #")  # , save=True)
    plotting.plotMultiWithErrors("experiment1", title="experiment 1", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)

if __name__ == "__main__":
    setupMultithreading()
    try:
        run(1e1)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")
