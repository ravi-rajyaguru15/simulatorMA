# 1. rmsprop optimiser? estimation instead of classification: mse, linear activation output
# 2. confusion matrix + balancing training data


# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.experiments.scenario import REGULAR_SCENARIO_ROUND_ROBIN
from sim.tasks.tasks import HARD
from sim.learning.agent.dqnAgent import dqnAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.simulations.SimpleSimulation import SimpleSimulation
import numpy as np
np.set_printoptions(suppress=True, precision=2)
import multiprocessing
from sklearn import metrics
from sklearn.utils import class_weight



# %%

CLASSIFICATION = False
MAX_JOBS = 5
NUM_ENERGY_STATES = 5
if CLASSIFICATION:
    LOSS = ['categorical_crossentropy']
else:
    LOSS = ['mse']

# %%

# create table agent for training data
tableExp = SimpleSimulation(numDevices=2, maxJobs=MAX_JOBS, agentClass=minimalTableAgent, tasks=[
                            HARD], systemStateClass=minimalSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=True, numEnergyLevels=NUM_ENERGY_STATES, trainClassification=CLASSIFICATION)
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
# print(NUM_SAMPLES, state.uniqueStates)
maxJobs = state.maxJobs
numBatteryLevels = state.singlesDiscrete['energyRemaining']
agent = tableExp.sharedAgent
agent.setProductionMode()

trainingData = np.zeros((NUM_SAMPLES, len(state.singles)))
if CLASSIFICATION:
    trainingTarget = np.zeros((NUM_SAMPLES, ), dtype=np.int)
else:
    trainingTargetOneHot = np.zeros((NUM_SAMPLES, tableExp.sharedAgent.numActions), dtype=np.int)

for i in range(NUM_SAMPLES):
    # chosenJobs = np.random.randint(0, maxJobs)
    # chosenBatteryLevel = np.random.randint(0, numBatteryLevels)

    # chooseState(state, chosenJobs, chosenBatteryLevel)
    state = state.fromIndex(i)

    # get correct action

    # add to datasets
    trainingData[i, :] = np.array(state.currentState)
    if CLASSIFICATION:
        action = agent.selectAction(state.currentState)
        trainingTarget[i] = action
    else:
        trainingTargetOneHot[i] = agent.predict(state)
# if CLASSIFICATION:
#     print(trainingTarget)
# else:
    # print(trainingTargetOneHot)

# import matplotlib.pyplot as pp
# pp.plot([0, 1], [0, 1])
# pp.show()

# convert targets to classifications
if CLASSIFICATION:
    trainingTargetOneHot = np.eye(agent.numActions)[trainingTarget]
    class_weights = class_weight.compute_class_weight(
        'balanced', np.unique(trainingTarget), trainingTarget)
    class_weights_dict = dict()
    for i in range(len(np.unique(trainingTarget))):
        class_weights_dict[i] = class_weights[i]
else:
    class_weights_dict = None
# class_weights_dict = None
# trainingData[:, 0] /= maxJobs
# trainingData[:, 1] /= numBatteryLevels
# print(trainingData)
# print(trainingTarget)

# %%


def singleThread(ID, depth, width, loss, results):
    # create deep agent for learning
    dqnExp = SimpleSimulation(numDevices=2, maxJobs=MAX_JOBS, agentClass=dqnAgent, tasks=[
                              HARD], systemStateClass=minimalSystemState, scenarioTemplate=REGULAR_SCENARIO_ROUND_ROBIN, centralisedLearning=True, numEnergyLevels=NUM_ENERGY_STATES, trainClassification=CLASSIFICATION)
    dqnExp.setBatterySize(1e-1)
    dqnExp.setFpgaIdleSleep(1e-3)

    # %%
    # train deep agent
    deepAgent = dqnExp.sharedAgent
    deepAgent.loss = loss
    deepAgent.createModel(depth, width)

    deepAgent.fit(trainingData, trainingTargetOneHot, epochs=100,
                  split=0.0, class_weights=class_weights_dict)
    if CLASSIFICATION:
        output = deepAgent.model.evaluate(trainingData, trainingTargetOneHot, verbose=0)
    else:
        output = deepAgent.fullModel.evaluate(trainingData,         trainingTargetOneHot.argmax(axis=1), verbose=0)
    predictions = deepAgent.model.predict_on_batch(trainingData)
    # print("evaluate: ", ID, output)
    if CLASSIFICATION: 
        print(metrics.confusion_matrix(
        trainingTarget, predictions.argmax(axis=1)))

    # full estimate
    # print(deepAgent.model.predict_on_batch(trainingData))
    # print(deepAgent.fullModel.predict_on_batch(trainingData))

    # deepAgent.model.summary()
    # deepAgent.fullModel.summary()

    results.put((depth, width, loss, output[1]))

# print(deepAgent.predict(deepAgent.model, state.currentState))


NUM_THREADS = 16
processes = []
results = multiprocessing.Queue()
for i in range(NUM_THREADS):
    for depth in [1,2,3,4,5,6,7,8]:
        for width in [2,4,6,8,10,12]:
            for loss in LOSS:
                newprocess = multiprocessing.Process(
                    target=singleThread, args=(i, depth, width, loss, results, ))
                newprocess.start()
                processes.append(newprocess)

print("\n\nresults:")
collected = dict()
for i in range(len(processes)):

    # processes[i].join()
    result = results.get()
    identifier = (result[2], result[0], result[1])
    if identifier not in collected:
        collected[identifier] = []
    collected[identifier].append(result[3])

processed = dict()
# print(collected)
for key in collected:
    avg = np.max(collected[key])
    if avg not in processed:
        processed[avg] = []
    processed[avg].append(key)

keys = list(processed.keys())
keys.sort()
# print(keys)
for key in keys:
    print(key, processed[key])
