import sys
import traceback

import sim.debug as debug
import sim.simulations.constants as constants
from sim.learning.agent.minimalAgent import minimalAgent
from sim.learning.state.minimalSystemState import minimalSystemState
from sim.offloading.offloadingPolicy import *
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation
from sim.tasks.tasks import HARD, EASY


def run():
	print("testing simple simulation")
	constants.NUM_DEVICES = 2
	constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1e2
	constants.OFFLOADING_POLICY = REINFORCEMENT_LEARNING
	debug.enabled = True
	debug.learnEnabled = True
	constants.DRAW_DEVICES = False
	taskOptions = [EASY, HARD]
	exp = Simulation(systemStateClass=minimalSystemState, agentClass=minimalAgent, tasks=taskOptions, autoJobs=True)

	numjobs = int(1e5)

	finishedJobs = dict()
	for task in taskOptions: finishedJobs[task] = 0
	try:
		# for i in range(numjobs):
		# 	exp.createNewJob(exp.devices[0])

		# for i in range(10):
		# 	exp.simulateTick()

		# for i in range(numjobs):
		# 	exp.simulateUntilJobDone()
		# 	finishedJobs[exp.getLatestFinishedJob().currentTask] += 1

		# exp.simulateUntilTime(50)

		exp.simulateEpisode()
		print("finished jobs:", exp.finishedTasks)

	# try:
	# 	exp.simulateEpisode()
	# 	print("Experiment done!", exp.time)
	# except Exception:
	# 	print("number of successful episodes:", exp.episodeNumber)
	# 	print(sys.exc_info())
	except:
		debug.printCache()
		traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
	run()