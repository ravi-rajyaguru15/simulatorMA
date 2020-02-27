import numpy as np

from sim import debug
from sim.learning.action import BATCH
from sim.learning.agent.qTableAgent import qTableAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.simulations.SimpleSimulation import SimpleSimulation, NEW_JOB
from sim.learning.state.discretisedSystemState import discretisedSystemState
from sim.tasks.job import job
from sim.tasks.tasks import EASY

exp = SimpleSimulation(numDevices=1, maxJobs=1, agentClass=qTableAgent, systemStateClass=minimalSystemState, autoJobs=False)
print("original:")
exp.sharedAgent.possibleActions = [BATCH]
exp.sharedAgent.numActions = 1
exp.sharedAgent.model.table = np.random.standard_normal(exp.sharedAgent.model.table.shape)
exp.sharedAgent.printModel()

dev = exp.devices[0]

for i in range(3):
	print()
	exp.processQueuedTask(0, (NEW_JOB, dev))
	exp.simulateTick()

	print("state:", exp.currentSystemState.currentState, dev.batchLength(EASY))

exp.sharedAgent.printModel()