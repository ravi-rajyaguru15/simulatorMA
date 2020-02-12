# check resulting job energy based on system state
from queue import PriorityQueue

import sim
from sim import debug
from sim.devices.components import powerPolicy
from sim.devices.platforms.platform import elasticNodev4
from sim.offloading import offloadingPolicy
from sim.simulations import constants
from sim.simulations.SimpleSimulation import SimpleSimulation as Simulation
import matplotlib.pyplot as pp

if __name__ == "__main__":
	constants.FPGA_POWER_PLAN = powerPolicy.STAYS_ON
	constants.OFFLOADING_POLICY = offloadingPolicy.REINFORCEMENT_LEARNING
	constants.NUM_DEVICES = 1
	elasticNodev4.BATTERY_SIZE = 1e0
	debug.enabled = False
	exp = Simulation()

	exp.simulate()

	# simulations done
	jobsList = PriorityQueue()
	for job in exp.finishedJobsList + exp.unfinishedJobsList:
		jobsList.put((job.id, job))

	# for i in range(10):
	# 	exp.simulateUntilJobDone()
	ylist = []
	xlist = []
	for num in range(jobsList.qsize()):
		job = jobsList.get()[1]

		beforeState = job.beforeState
		energyCost = job.totalEnergyCost * 1e3
		print("%s %s created: %.2f energy: %.4f %s" % (job, job.finished, job.createdTime, energyCost, beforeState.dictRepresentation))

		if job.finished:
			xlist.append(beforeState.dictRepresentation[""])
			ylist.append(job.totalEnergyCost)

	pp.plot(xlist, ylist)
	pp.show()