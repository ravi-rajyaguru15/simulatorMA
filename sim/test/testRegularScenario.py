from sim.experiments.scenario import REGULAR_SCENARIO_RANDOM, REGULAR_SCENARIO_ALL, REGULAR_SCENARIO_ROUND_ROBIN
from sim.simulations.SimpleSimulation import SimpleSimulation

for scenario in [REGULAR_SCENARIO_ALL]: #, REGULAR_SCENARIO_RANDOM, REGULAR_SCENARIO_ROUND_ROBIN]:
	print(scenario)
	exp = SimpleSimulation(numDevices=1, autoJobs=False, scenarioTemplate=scenario)
	exp.setBatterySize(1e-2)
	# exp.performScenario(REGULAR_SCENARIO_ROUND_ROBIN)

	# while exp.queue.qsize() > 0:
	# 	print(exp.queue.get())

	# for i in range():
		# exp.queueNextJob()
	exp.simulateQueuedTasks(reset=False)
		# print(exp.scenario.previousDevice, exp.scenario.previousDevice.currentTime)
	# print()

	del exp