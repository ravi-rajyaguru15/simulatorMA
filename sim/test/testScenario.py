from sim.experiments.scenario import ALL_SCENARIOS
from sim.simulations.SimpleSimulation import SimpleSimulation

for scenario in ALL_SCENARIOS:
	print(scenario)
	exp = SimpleSimulation(numDevices=2, scenarioTemplate=scenario)
	exp.setBatterySize(1e-1)
	# exp.performScenario(REGULAR_SCENARIO_ROUND_ROBIN)

	# while exp.queue.qsize() > 0:
	# 	print(exp.queue.get())

	# for i in range():
	# exp.queueNextJob()
	exp.simulateQueuedTasks(reset=False)
	# print(exp.scenario.previousDevice, exp.scenario.previousDevice.currentTime)
	print()

	del exp