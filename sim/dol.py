import numpy as np
import math

'''
Division of labor Index by Gorelick et al. -- 2004
'''


def DOL(devices, tasks):
    # Step 1:  create a matrix that is n x m, where n is the number of rows
    # and m is the number of columns.  Each row represents an individual
    # in the population, each column represents a task.  For the purposes
    # of this experiment, n = 10 and m = 9.
    numAgents = len(devices)
    numThetas = len(tasks)
    # dataMatrix = np.zeros((len(devices), len(tasks) + 1))  # not +1 because no idle matrix that is number of individuals x number of tasks
    dataMatrix = np.zeros((len(devices), len(tasks)))  # not +1 because no idle matrix that is number of individuals x number of tasks
    totalTasks = 0
    # now we need to populate the matrix per individual
    for i in range(0, len(devices)):
        # tCounts = Counter(oneColony[i].getJobs())

        for j in range(0, numThetas):
            tCount = devices[i].fpga.getConfigTime(tasks[j])
            # tCount = devices[i].getNumTasksDone(tasks[j])

            dataMatrix[i][j] = tCount
            totalTasks += tCount
        # dataMatrix[i][numThetas] = devices[i].currentTime - np.sum(dataMatrix[i][:-1])
        # totalTasks += dataMatrix[i][numThetas]

    print()
    print(dataMatrix)


    # Step 2:  Normalize the matrix by dividing every cell by the total number of tasks
    dataMatrix = dataMatrix * (1 / totalTasks)

    print(dataMatrix)

    # Step 3:  Build probability data structures
    xProbs = np.ones(numThetas)  # number of tasks in length
    yProbs = np.ones(numAgents)  # number of agents in length
    yProbs = yProbs * (
                1 / numAgents)  # vector of probabilities for each individual (as they don't die, this stays constant for each and are equally likely to be encountered)
    xProbs = np.array(
        [sum(x) for x in zip(*dataMatrix)])  # vector of probabilities for each task, should be numThetas long

    # Step 4:  Build mutual entropy evaluations
    entropyX = 0
    for i in range(0, len(xProbs)):
        if xProbs[i] != 0:
            entropyX += xProbs[i] * math.log(xProbs[i])
    entropyX = -1 * entropyX

    if entropyX < 0:  # if all tasks are 'None', this occurs
        entropyX = 0

    entropyY = 0
    for i in range(0, len(yProbs)):  # H(Y)
        if yProbs[i] != 0:
            entropyY += yProbs[i] * math.log(yProbs[i])
    entropyY = -1 * entropyY

    # Calculate I(X,Y)
    totalI = 0
    for i in range(0, len(yProbs)):  # for each individual
        for j in range(0, len(xProbs)):  # for each task per individual
            probXY = dataMatrix[i][j]  # probability of finding this individual doing this task
            probX = xProbs[j]  # probability of the task
            probY = yProbs[i]  # probability of encountering individual
            if probXY != 0 and probX != 0 and probY != 0:
                totalI += probXY * math.log(probXY / (probX * probY))

    # We can now calcuate the DOLs - be aware of bad entropy values (i.e. = 0 which can occur)
    # Also taking into account when we get an incredibly low (but positive) entropyX score
    # This apparently happens when 1 agent does 1 task but everyone else remains idle
    if entropyX != 0 and totalI < entropyX:
        DOL_IND_TASK = totalI / entropyX
    else:
        DOL_IND_TASK = 0

    if entropyY != 0:
        DOL_TASK_IND = totalI / entropyY
    else:
        DOL_TASK_IND = 0

    print(DOL_IND_TASK)

    return DOL_IND_TASK, DOL_TASK_IND  # , DOL_SYMM