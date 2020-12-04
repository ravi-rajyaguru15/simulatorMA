# 1. rmsprop optimiser? estimation instead of classification: mse, linear activation output
# 2. confusion matrix + balancing training data


# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow.python.util.deprecation as deprecation
deprecation._PRINT_DEPRECATION_WARNINGS = False
import glob
import shutil
import os.path
import keras.models
from sklearn.utils import class_weight
from sklearn import metrics
import multiprocessing
import numpy as np
from sim.simulations import localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.learning.agent.dqnAgent import dqnAgent
from sim.tasks.tasks import HARD
from sim.experiments.scenario import REGULAR_SCENARIO_ROUND_ROBIN
from sim.learning.state.minimalSystemState import minimalSystemState

np.set_printoptions(suppress=True, precision=2)


# from tensorflow.python.client import device_lib
# print(device_lib.list_local_devices())

# %%
CLASSIFICATION = True
MAX_JOBS = 5
NUM_ENERGY_STATES = 3
if CLASSIFICATION:
    # LOSS = ['mse']
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

trainingData = []
# trainingData = np.zeros((NUM_SAMPLES, len(state.singles)))
if CLASSIFICATION:
    trainingTarget = []
    # trainingTarget = np.zeros((NUM_SAMPLES, ), dtype=np.int)
else:
    trainingTargetOneHot = []
    # trainingTargetOneHot = np.zeros((NUM_SAMPLES, tableExp.sharedAgent.numActions), dtype=np.int)

for i in range(NUM_SAMPLES):
    # chosenJobs = np.random.randint(0, maxJobs)
    # chosenBatteryLevel = np.random.randint(0, numBatteryLevels)

    # chooseState(state, chosenJobs, chosenBatteryLevel)
    state = state.fromIndex(i)

    # get correct action

    # checking if state has clear winner
    qvalues = agent.predict(state)
    unique, counts = np.unique(qvalues, return_counts=True) 
    print(qvalues, unique, counts, counts[np.argmax(unique)])
    if counts[np.argmax(unique)] == 1:
        # add to datasets
        # trainingData[i, :] = np.array(state.currentState)
        trainingData.append(np.array(state.currentState))
        if CLASSIFICATION:
            action = agent.selectAction(state.currentState)
            # trainingTarget[i] = action
            trainingTarget.append(action)
        else:
            # trainingTargetOneHot[i] = agent.predict(state)
            trainingTargetOneHot.append(agent.predict(state))

print("Training reduced from", state.getUniqueStates(), "to", len(trainingData))

trainingData = np.array(trainingData)
if CLASSIFICATION:
    trainingTarget = np.array(trainingTarget)
else:
    trainingTargetOneHot = np.array(trainingTargetOneHot)

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
    for i in range(tableExp.sharedAgent.numActions):
        if i in class_weights:
            class_weights_dict[i] = class_weights[i]
        else:
            class_weights_dict[i] = 0
    class_weights_dict = None  # DISABLE WEIGHT BALANCE
else:
    class_weights_dict = None
# class_weights_dict = None
# trainingData[:, 0] /= maxJobs
# trainingData[:, 1] /= numBatteryLevels
# print(trainingData)
# print(trainingTarget)

# %%


def singleThread(ID, depth, width, loss, epochs, results):
    # import tensorflow as tf
    # import tensorflow.config.gpu
    # tf.config.gpu.set_per_process_memory_growth(True)
    # tf.debugging.set_log_device_placement(True)

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

    deepAgent.fit(trainingData, trainingTargetOneHot, epochs=epochs,
                  split=0.0, class_weights=class_weights_dict)
    if CLASSIFICATION:
        output = deepAgent.model.evaluate(
            trainingData, trainingTargetOneHot, verbose=0)
    else:
        output = deepAgent.fullModel.evaluate(
            trainingData,         trainingTargetOneHot.argmax(axis=1), verbose=0)
    predictions = deepAgent.model.predict_on_batch(trainingData)
    # print("evaluate: ", ID, output)
    if CLASSIFICATION:
        confusion = metrics.confusion_matrix(
            trainingTarget, predictions.argmax(axis=1))
    else:
        # print(trainingTargetOneHot.argmax(axis=1))
        onehot = np.eye(np.shape(trainingTargetOneHot)[1])[
            trainingTargetOneHot.argmax(axis=1)]
        # print(onehot)
        # print(deepAgent.fullModel.predict_on_batch(trainingData).argmax(axis=1))
        confusion = metrics.confusion_matrix(trainingTargetOneHot.argmax(
            axis=1), deepAgent.fullModel.predict_on_batch(trainingData).argmax(axis=1))

    # full estimate
    # print(deepAgent.model.predict_on_batch(trainingData))
    # print(deepAgent.fullModel.predict_on_batch(trainingData))

    # deepAgent.model.summary()
    # deepAgent.fullModel.summary()
    # print('done')
    deepAgent.saveModel(ID)
    result = (depth, width, loss, output[1], confusion, epochs, ID)
    # print(result)
    results.put(result)

# print(deepAgent.predict(deepAgent.model, state.currentState))


NUM_CPUS = 64
NUM_THREADS = 8
processes = []
results = multiprocessing.Queue()
ID = 0
for i in range(NUM_THREADS):
    for depth in [1, 2, 3, 4]:  # [1,2,3,4,5,6,7,8]:
        for width in [2, 4, 8, 10, 20]:  # [2,4,6,8,10,12]:
            for loss in LOSS:
                for epochs in [1, 10, 100, 1000, 10000]:  # 10, 50, 100, , 10000
                    newprocess = multiprocessing.Process(
                        target=singleThread, args=(ID, depth, width, loss, epochs, results, ))
                    ID += 1
                    # newprocess.start()
                    processes.append(newprocess)

print("total processes:", len(processes))
# print("initial processes")
index = 0
for i in range(min(NUM_CPUS, len(processes))):
    processes[i].start()
    index += 1

print("doing", index)

print("\n\nresults:")
collected = dict()
for i in range(len(processes)):

    # processes[i].join()\
    # print("waiting for result")
    result = results.get()
    # print("results", i)

    # start more if available
    if len(processes) > index:
        processes[index].start()
        index += 1
        # print("started", index)

    identifier = (result[2], result[0], result[1], result[5])
    if identifier not in collected:
        collected[identifier] = []
    collected[identifier].append((result[3], result[4], result[6]))

processed = dict()
# print(collected)
print("collected:")
print(collected.keys())
for key in collected:
    values = [things[0] for things in collected[key]]
    avg = np.max(values)
    bestresult = collected[key][np.argmax(values)]
    favourite = bestresult[1]  # this is confusion matrix
    bestid = bestresult[2]
    if avg not in processed:
        processed[avg] = []
    processed[avg].append((key, favourite, bestid))

keys = list(processed.keys())
keys.sort()
print("keys:")
print(keys)
for key in keys:
    acc, confusion, id = processed[key][0]
    print(key, acc, id)
    print(confusion)

print('winning id', id)
targetName = localConstants.OUTPUT_DIRECTORY + "dqnfullmodel.pickle"
if os.path.exists(targetName):
    shutil.rmtree(targetName)
os.rename(localConstants.OUTPUT_DIRECTORY +
          f"/dqnfullmodel{id}.pickle", targetName)

# delete unused models
models = glob.glob(localConstants.OUTPUT_DIRECTORY + "/dqnfullmodel*.pickle")
# models.remove(targetName)
print("avoid", targetName)
for file in models:
    if file != targetName:
        # print("delete", file)
        shutil.rmtree(file)
    # else:
    #     print("not delete", file)
