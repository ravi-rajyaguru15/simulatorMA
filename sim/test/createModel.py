# based on model from acsos experiment1

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import multiprocessing

import sys
import traceback

from sim import debug, counters, plotting
from sim.experiments.experiment import executeMulti
from sim.experiments.scenario import REGULAR_SCENARIO_ROUND_ROBIN
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.randomAgent import randomAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.simulations import localConstants, constants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.experiments.experiment import executeMulti, setupMultithreading

from sim.tasks.tasks import HARD, EASY

maxjobs = 5
numEnergyLevels = 3
CLASSIFICATION = True

print("starting experiment")

processes = list()
results = multiprocessing.Queue()
finished = multiprocessing.Queue()

localConstants.REPEATS = 1
# localConstants.REPEATS = 8
numEpisodes = int(1e3)
# agentsToTest = [minimalTableAgent]
minimalTableAgent # , localAgent]
agent = minimalTableAgent # [minimalAgent, lazyAgent]:
centralised = True
exp = SimpleSimulation(numDevices=4, maxJobs=maxjobs, agentClass=agent, tasks=[HARD], numEnergyLevels=numEnergyLevels, systemStateClass=minimalSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=centralised, trainClassification=CLASSIFICATION)
print(exp.currentSystemState.uniqueStates)
# exp.scenario.setInterval(1)
exp.setBatterySize(1e-1)
exp.setFpgaIdleSleep(1e-3)

e = None
try:
    print("running episodes")
    for e in range(numEpisodes):
        if e % 100 == 0: print ('.')
        debug.infoEnabled = False
        exp.simulateEpisode(e)

        # results.put(["%s %s" % (exp.devices[0].agent.__name__, "Centralised" if centralised else "Decentralised"), e, exp.numFinishedJobs])
except:
    debug.printCache()
    traceback.print_exc(file=sys.stdout)
    print(agent, e)
    print("Error in experiment:", exp.time)
    sys.exit(0)

exp.sharedAgent.saveModel()