
import multiprocessing

import sys
import traceback
import numpy as np

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
from sim.experiments.experiment import executeMulti, setupMultithreading, assembleResultsBasic

from sim.tasks.tasks import HARD
maxjobs = 5
numEnergyStates = 3

def runThread(numEpisodes, results, finished):
    dqnExp = SimpleSimulation(numDevices=2, maxJobs=maxjobs, agentClass=dqnAgent, tasks=[HARD], systemStateClass=minimalSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=True, numEnergyLevels=numEnergyStates, trainClassification=False)
    # exp.scenario.setInterval(1)
    dqnExp.sharedAgent.loadModel()
    # dqnExp.sharedAgent.fullModel.summary()
    # dqnExp.sharedAgent.model.summary()
    dqnExp.sharedAgent.setProductionMode()
    dqnExp.setBatterySize(1e-1)
    dqnExp.setFpgaIdleSleep(1e-3)

    tableExp = SimpleSimulation(numDevices=2, maxJobs=maxjobs, agentClass=minimalTableAgent, tasks=[HARD], systemStateClass=minimalSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=True, numEnergyLevels=numEnergyStates, trainClassification=False)
    # exp.scenario.setInterval(1)
    tableExp.sharedAgent.loadModel()
    tableExp.sharedAgent.setProductionMode()
    tableExp.setBatterySize(1e-1)
    tableExp.setFpgaIdleSleep(1e-3)
    

    print("states:", tableExp.sharedAgent.systemState.uniqueStates)
    duplicates = []
    # iterate through possible states
    for i in range(tableExp.sharedAgent.systemState.uniqueStates):
        # set state in both experiments

        state = tableExp.sharedAgent.systemState.fromIndex(i)

        # table
        agentName = tableExp.sharedAgent.__name__
        qvalues = tableExp.sharedAgent.predict(state)
        print(np.where(qvalues == np.max(qvalues))[0])
        if np.where(qvalues == np.max(qvalues))[0].shape[0] > 1:
            duplicates.append(i)
        for j in range(tableExp.sharedAgent.numActions):
            result = [f"{agentName} {j}", i, qvalues[j]]
            results.put(result)

        # dqn 
        agentName = dqnExp.sharedAgent.__name__
        qvalues = dqnExp.sharedAgent.predict(dqnExp.sharedAgent.model, state.currentState)
        for j in range(dqnExp.sharedAgent.numActions):
            result = [f"{agentName} {j}", i, qvalues[j]]
            results.put(result)
        # results.put([f"{agentName}", e, exp.getCurrentTime()])

    print("DUPLICATES", duplicates)
# except:
#     debug.printCache()
#     traceback.print_exc(file=sys.stdout)
#     print(agent, e)
#     print("Error in experiment :", exp.time)
#     sys.exit(0)

    finished.put(True)

def run(numEpisodes):
    print("starting experiment")

    processes = list()
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()

    localConstants.REPEATS = 2
    # localConstants.REPEATS = 8
    numEpisodes = int(numEpisodes)
    # agentsToTest = [minimalTableAgent]
    agentsToTest = [dqnAgent] # minimalTableAgent, , localAgent]
    for _ in range(localConstants.REPEATS):
        processes.append(multiprocessing.Process(target=runThread, args=(numEpisodes, results, finished)))

    results = executeMulti(processes, results, finished, numResults=len(processes) * numEnergyStates * 3 * (maxjobs + 1) * 2)

    # plotting.plotMultiWithErrors("experiment1", title="experiment 1", results=results, ylabel="", xlabel="Episode #")  # , save=True)
    plotting.plotMultiWithErrors("experiment1", title="experiment 1", results=results, ylabel="Q Value", xlabel="State Index")  # , save=True)

if __name__ == "__main__":
    setupMultithreading()
    try:
        run(1e1)
    except:
        traceback.print_exc(file=sys.stdout)

        print("ERROR")
