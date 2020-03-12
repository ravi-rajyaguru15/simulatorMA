# initial train
import pickle
import os
import random
import sys
import numpy as np

from sim.learning.agent.lazyDeepAgent import lazyDeepAgent
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.simulations import constants
from sim.simulations.SimpleSimulation import SimpleSimulation

def compareModels(correct, uut):
	true = 0
	tested = 0
	# for i in range(100):
	numToTest = int(correct.currentSystemState.getUniqueStates())
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
		# print(correct.sharedAgent.model.getQ(index), uut.sharedAgent.predict(uut.sharedAgent.model, currentState))
		# print(correctAction, uutAction)

		if not all(correct.sharedAgent.model.getQ(index) == 25.):
			if correctAction == uutAction:
				true += 1
			tested += 1

	print("\tModels match:", float(true) / tested * 100., )


exp1 = SimpleSimulation(agentClass=lazyTableAgent)
if not exp1.sharedAgent.loadModel():
	print("Training table agent")
	constants.CENTRALISED_LEARNING = True
	exp1.setBatterySize(1e-2)
	for i in range(1):
		exp1.simulateEpisode()
	print("Saving...")
	exp1.sharedAgent.saveModel()
exp1.sharedAgent.setProductionMode()

exp2 = SimpleSimulation(agentClass=lazyDeepAgent)
exp2.sharedAgent.setProductionMode()

# print(exp2.sharedAgent.systemState.stateCount)

quiet = True
numIterations = 2000
# index = 0
# for i in range(2): # exp1.currentSystemState.getUniqueStates()):
# 	print(i, exp1.currentSystemState.fromIndex(i).currentState, exp1.currentSystemState.fromIndex(i).dictRepresentation)
# 	pass

totest = int(exp1.currentSystemState.getUniqueStates())
for j in range(numIterations):
	for i in range(totest):
	# for i in range(exp1.currentSystemState.getUniqueStates() * numIterations):
		# for j in range(100):
		# generate index
		# index = i
		# index = random.randint(0, exp1.currentSystemState.getUniqueStates() - 1)
		index = random.randint(0, totest - 1)

		sys.stdout.write("\rProgress: %.2f%%" % ((totest * j + (i+1)) / (totest * numIterations) * 100.))
		# sys.stdout.write("\rProgress: %.2f%%" % ((i+1) / (totest) * 100.))
		beforeState = exp1.currentSystemState.fromIndex(index).currentState

		action = random.randint(0, exp1.sharedAgent.numActions-1)
		# for action in range(exp1.sharedAgent.numActions):
		# action = exp1.sharedAgent.selectAction(beforeState)
		reward = exp1.sharedAgent.model.getQ(index)[action]
		finished = False
		# print(action, reward)
		exp2.sharedAgent.trainModel(action, reward, beforeState, None, finished)
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

	if j % 100 == 0:
		compareModels(exp1, exp2)
	# 	print(totest)
	# 	for i in range(totest):
	# 		# print(exp1.currentSystemState.fromIndex(i).currentState)
	# 		print(np.array(exp1.sharedAgent.model.getQ(i)), np.array(exp2.sharedAgent.predict(exp2.sharedAgent.model, exp1.currentSystemState.fromIndex(i).currentState)))
	# 	print()
	# 	print()

exp2.sharedAgent.saveModel()
compareModels(exp1, exp2)