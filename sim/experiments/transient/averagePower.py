import multiprocessing
import sys
import traceback

from sim.simulation import simulation

import sim.debug
import sim.experiments.experiment
import sim.plotting
import sim.simulations.constants
import sim.simulations.variable

numDevices = 1
jump = 1
totalTime = 1e2
def runThread(alpha, results, finished):
	# sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)
	sim.simulations.constants.EXPECTED_LIFETIME_ALPHA = alpha
	exp = simulation(hardwareAccelerated=True)
	sim.simulations.current = exp
	for i in range(int(totalTime/jump)):
		exp.simulateTime(jump)
		results.put(["", i * jump, exp.devicesLifetimes()])
		print("\ttime", exp.time, "lifetime", exp.systemLifetime())
		print([dev.expectedLifetime() for dev in exp.devices])
		print([dev.averagePower for dev in exp.devices])
	
	finished.put(True)

def run():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.simulations.constants.SAMPLE_SIZE = sim.simulations.variable.Gaussian(10, 2)
	sim.simulations.constants.SAMPLE_RAW_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.SAMPLE_PROCESSED_SIZE = sim.simulations.variable.Constant(4, integer=True)
	sim.simulations.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF
	sim.simulations.constants.OFFLOADING_POLICY = sim.offloadingPolicy.ANYTHING
	sim.simulations.constants.JOB_LIKELIHOOD = 5e-3
	sim.simulations.constants.MINIMUM_BATCH = 10
	sim.simulations.constants.DEFAULT_ELASTIC_NODE.BATTERY_SIZE = 1

	processes = list()
	
	# offloadingOptions = [True, False]
	results = multiprocessing.Queue()
	finished = multiprocessing.Queue()
	sim.simulations.constants.REPEATS = 1

	# for alpha in np.logspace(-4, -3, num=2, endpoint=True):
	alpha = 1e-3
	if True:
		for _ in range(sim.simulations.constants.REPEATS):
			processes.append(multiprocessing.Process(target=runThread, args=(alpha, results, finished)))
	
	results = sim.experiments.experiment.executeMulti(processes, results, finished, numResults=int(totalTime/jump * len(processes)))
	print ('plot time')
	sim.plotting.plotMultiWithErrors("expectedLife", results=results) # , save=True)

try:
	run()
except:
	traceback.print_exc(file=sys.stdout)

	print ("ERROR")