import numpy as np

from sim.learning.agent.qTableAgent import qTableAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.learning.state.discretisedSystemState import discretisedSystemState

exp = SimpleSimulation(numDevices=1, maxJobs=1, agentClass=qTableAgent, systemStateClass=minimalSystemState)
state = exp.currentSystemState
testAgent = exp.sharedAgent

testAgent.model.table = np.random.standard_normal(testAgent.model.table.shape)
# testAgent.model.setQ(state=0, action=0, value=1)
# testAgent.model.setQ(state=5, action=2, value=2)
# testAgent.model.setQ(state=10, action=1, value=3)
testAgent.printModel()

newState = minimalSystemState(numDevices=1, maxJobs=2)
newAgent = qTableAgent(newState)
newAgent.setDevices(exp.devices)
newAgent.importQTable(testAgent)
# newAgent.printModel()

# mapping = discretisedSystemState.convertIndexMap(state, newState)
# for i in range(len(mapping)):
# 	newAgent.model.setQ(mapping[i], testAgent.model.getQ(i))

newAgent.printModel()

# for i in range(state.getUniqueStates()):
# 	print(state.fromIndex(i))
	# newAgent.model.setQ(newState., testAgent.model.getQ(i))
