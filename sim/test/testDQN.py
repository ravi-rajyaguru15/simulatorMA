# initial train
import pickle
import os
import random
import sys
import numpy as np

from sim import plotting
from sim.learning.agent.lazyDeepAgent import lazyDeepAgent
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.simulations import constants, localConstants
from sim.simulations.SimpleSimulation import SimpleSimulation
import matplotlib.pyplot as pp

def compareModels(correct, uut):
	true = 0
	tested = 0
	# for i in range(100):
	numToTest = int(correct.currentSystemState.getUniqueStates())
	errors = []
	for i in range(numToTest):
		# index = random.randint(0, correct.currentSystemState.getUniqueStates() - 1)
		index = i
		state = correct.currentSystemState.fromIndex(index)
		currentState = state.currentState
		# print(state, currentState, index)

		correct.currentSystemState = state
		uut.currentSystemState = state

		correctAction = correct.sharedAgent.selectAction(currentState)
		uutAction = uut.sharedAgent.selectAction(currentState)

		correctQ = correct.sharedAgent.model.getQ(state)
		# print("correctQ", correctQ)
		uutQ = uut.sharedAgent.predict(uut.sharedAgent.model, currentState)
		# print("uutQ", uutQ)

		error = uutQ - correctQ
		# print("error", error)
		# print(np.mean(error))
		errors.append(error)

		# print(correct.sharedAgent.model.getQ(index), uut.sharedAgent.predict(uut.sharedAgent.model, currentState))
		# print(correctAction, uutAction)

		if not all(correct.sharedAgent.model.getQ(index) == 25.):
			if correctAction == uutAction:
				true += 1
			tested += 1

	# print("\tModels match:", float(true) / tested * 100., )

	return float(true) / tested * 100., np.average(errors)

exp1 = SimpleSimulation(agentClass=lazyTableAgent)
if not exp1.sharedAgent.loadModel():
	print("Training table agent")
	constants.CENTRALISED_LEARNING = True
	exp1.setBatterySize(1e-1)
	trainingRuns = int(1e3)
	for i in range(trainingRuns):
		sys.stdout.write("\r%.2f %%" % (i / trainingRuns * 100.))
		exp1.simulateEpisode()
	print("Saving...")
	exp1.sharedAgent.saveModel()
	exp1.sharedAgent.printModel()
exp1.sharedAgent.setProductionMode()

exp2 = SimpleSimulation(agentClass=lazyDeepAgent)
exp2.sharedAgent.setProductionMode()

quiet = True
numIterations = int(1e5)

matchingList = []
losses = []
errors = []
totest = int(exp1.currentSystemState.getUniqueStates())
for j in range(numIterations):
	for i in range(totest):
		index = random.randint(0, totest - 1)

		beforeState = exp1.currentSystemState.fromIndex(index).currentState

		action = random.randint(0, exp1.sharedAgent.numActions-1)
		# for action in range(exp1.sharedAgent.numActions):
		# action = exp1.sharedAgent.selectAction(beforeState)
		reward = exp1.sharedAgent.model.getQ(index)[action]
		finished = False
		# print(action, reward)
		exp2.sharedAgent.trainModel(action, reward, beforeState, None, finished)
		# print("loss:", exp2.sharedAgent.latestLoss)
		losses.append(exp2.sharedAgent.latestLoss)
		# print("prediction:", exp2.sharedAgent.predict(exp2.sharedAgent.model, beforeState))
		# if not quiet:
			# print("finished", finished)
		# print("index", index, beforeState)
		# print("action", action)
		# print("reward", reward)
		# print("index:     ", index)
		# print("Q          ", exp1.sharedAgent.model.getQ(index))
		# print("prediction:", exp2.sharedAgent.predict(exp2.sharedAgent.model, beforeState))
		# print("actions:   ", exp1.sharedAgent.selectAction(beforeState), exp2.sharedAgent.selectAction(beforeState))

	if j % int(numIterations / 100.) == 0:
		# sys.stdout.write("\rProgress: %.2f%%" % ((totest * j + (i+1)) / (totest * numIterations) * 100.))
		print("Progress: %.2f %%" % (j / float(numIterations / 100.)))
		correct, error = compareModels(exp1, exp2)
		matchingList.append(correct)
		errors.append(error)
	# 	print(totest)
	# 	for i in range(totest):
	# 		# print(exp1.currentSystemState.fromIndex(i).currentState)
	# 		print(np.array(exp1.sharedAgent.model.getQ(i)), np.array(exp2.sharedAgent.predict(exp2.sharedAgent.model, exp1.currentSystemState.fromIndex(i).currentState)))
	# 	print()
	# 	print()

pp.figure(1)
pp.plot(range(len(matchingList)), matchingList)
pp.title("DQN Direct Training")
pp.xlabel("Training %")
pp.ylabel("Percentage matching actions")
pp.grid()
if localConstants.DRAW_GRAPH:
	pp.show()
if localConstants.SAVE_GRAPH:
	plotting.saveFig("dqn direct training")

pp.figure(2)
pp.plot(range(len(losses)), losses)
pp.title("DQN Direct Training Loss")
pp.xlabel("Training %")
pp.ylabel("Losses")
pp.grid()
if localConstants.DRAW_GRAPH:
	pp.show()
if localConstants.SAVE_GRAPH:
	plotting.saveFig("dqn direct training loss")

pp.figure(3)
pp.plot(range(len(errors)), errors)
pp.title("DQN Direct Training Errors")
pp.xlabel("Training %")
pp.ylabel("Error")
pp.grid()
if localConstants.DRAW_GRAPH:
	pp.show()
if localConstants.SAVE_GRAPH:
	plotting.saveFig("dqn direct training error")

exp2.sharedAgent.saveModel()
compareModels(exp1, exp2)