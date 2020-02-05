
def testRepeatsThread(name, samples, resultsQueue):
	sim.constants.SAMPLE_SIZE = sim.variable.Constant(samples)

	exp = simulation(0, 1, 0)

	exp.simulateTime(sim.constants.PLOT_TD * 10)
	exp.devices[0].createNewJob(exp.time, hardwareAccelerated=False)
	exp.simulateTime(sim.constants.PLOT_TD * 1500)
	if not exp.allDone():
	
		raise Exception("not all devices done: {}".format(samples))
	# print ('repeat', i, 'done')
	
	resultsQueue.put([name, samples, np.sum(exp.totalDevicesEnergy())])

	# test that sim.constants are still set correctly
	assert(sim.constants.SAMPLE_SIZE.gen() == samples)
	
def testRepeats():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.LOCAL_ONLY
	sim.constants.MINIMUM_BATCH = 1
	sim.constants.JOB_LIKELIHOOD = 0
	
	REPEATS = 16

	# results = list()
	samplesList = range(1, 100, 10)

	processes = list()
	results = multiprocessing.Queue()
	numThreads = REPEATS * len(samplesList)
	for i in range(REPEATS):
		for samples in samplesList:
			processes.append(multiprocessing.Process(target=testRepeatsThread, args=("Repeats", samples, results)))
	
	for process in processes: process.start()
	for process in processes: process.join()

	sim.plotting.plotMultiWithErrors("testRepeats", results=assembleResults(numThreads, results))
