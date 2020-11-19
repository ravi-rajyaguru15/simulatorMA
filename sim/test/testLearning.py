# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import numpy as np


# %%
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.dqnAgent import dqnAgent
from sim.tasks.tasks import HARD
from sim.experiments.scenario import REGULAR_SCENARIO_ROUND_ROBIN
from sim.learning.state.minimalSystemState import minimalSystemState


# %%

# create table agent for training data
tableExp = SimpleSimulation(numDevices=2, maxJobs=5, agentClass=minimalTableAgent, tasks=[HARD],systemStateClass=minimalSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=True)
tableExp.sharedAgent.loadModel()
tableExp.setBatterySize(1e-1)
tableExp.setFpgaIdleSleep(1e-3)


# %%
def chooseState(state, chosenJobs, chosenBatteryLevel):
    state = tableExp.sharedAgent.systemState 
    maxJobs = state.maxJobs
    numBatteryLevels = state.singlesDiscrete['energyRemaining']
    
    state.setField('jobsInQueue', chosenJobs / maxJobs)
    state.setField('energyRemaining', chosenBatteryLevel / numBatteryLevels)


# %%
# prepare training and testing data
state = tableExp.sharedAgent.systemState 
# NUM_SAMPLES = 100 * state.uniqueStates
NUM_SAMPLES = state.uniqueStates
print(NUM_SAMPLES, state.uniqueStates)
maxJobs = state.maxJobs
numBatteryLevels = state.singlesDiscrete['energyRemaining']
agent = tableExp.sharedAgent
agent.setProductionMode()

trainingData = np.zeros((NUM_SAMPLES, len(state.singles)))
trainingTarget = np.zeros((NUM_SAMPLES, ), dtype=np.int)

for i in range(NUM_SAMPLES):
    # chosenJobs = np.random.randint(0, maxJobs)
    # chosenBatteryLevel = np.random.randint(0, numBatteryLevels)

    # chooseState(state, chosenJobs, chosenBatteryLevel)
    state = state.fromIndex(i)

    # get correct action
    action = agent.selectAction(state.currentState)

    # add to datasets
    trainingData[i, :] = np.array(state.currentState)
    trainingTarget[i] = action

# import matplotlib.pyplot as pp
# pp.plot([0, 1], [0, 1])
# pp.show()

# convert targets to classifications
trainingTarget = np.eye(agent.numActions)[trainingTarget]
# trainingData[:, 0] /= maxJobs
# trainingData[:, 1] /= numBatteryLevels
print(trainingData)
print(trainingTarget)

# %%

# create deep agent for learning
dqnExp = SimpleSimulation(numDevices=2, maxJobs=5, agentClass=dqnAgent, tasks=[HARD],systemStateClass=minimalSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=True)
dqnExp.setBatterySize(1e-1)
dqnExp.setFpgaIdleSleep(1e-3)


# %%
# train deep agent
deepAgent = dqnExp.sharedAgent
deepAgent.model.summary()
# deepAgent.model.compile()
# print(deepAgent.trainable_model)
# deepAgent.createModel()
# deepAgent.model.summary()
# deepAgent.trainModelBatch(trainingData, trainingTarget)
deepAgent.fit(trainingData, trainingTarget, epochs=100, split=0.0)
print("evaluate: ", deepAgent.model.evaluate(trainingData, trainingTarget))

# print(deepAgent.predict(deepAgent.model, state.currentState))



