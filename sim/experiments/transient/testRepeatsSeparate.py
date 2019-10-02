
def testRepeatsSeparateThread(i, jobLikelihood, resultsQueue):
	sim.constants.JOB_LIKELIHOOD = jobLikelihood
	
	exp = simulation(hardwareAccelerated=False)
	exp.simulateTime(10)

	if not exp.allDone():
		warnings.warn("not all devices done: {}".format(jobLikelihood))

	resultsQueue.put(["Repeat " + str(i), jobLikelihood, (np.average([dev.totalSleepTime for dev in exp.devices]), 0)])
	

def testRepeatsSeparate():
	print ("starting experiment")
	sim.debug.enabled = False
	sim.constants.OFFLOADING_POLICY = sim.offloadingPolicy.RANDOM_PEER_ONLY # sim.offloadingPolicy.LOCAL_ONLY
	sim.constants.MINIMUM_BATCH = 5
	# sim.constants.JOB_LIKELIHOOD = 0
	sim.constants.SAMPLE_RAW_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.SAMPLE_PROCESSED_SIZE = sim.variable.Constant(4, integer=True)
	sim.constants.FPGA_POWER_PLAN = sim.powerPolicy.IMMEDIATELY_OFF

	REPEATS = 6

	# results = list()
	sim.constants.SAMPLE_SIZE = sim.variable.Gaussian(10, 2)

	# pool = multiprocessing.pool.ThreadPool(12)
	processes = list()
	results = multiprocessing.Queue()
	# numThreads = REPEATS * len(samplesList)
	for i in range(REPEATS):
		# samplesList = range(1, 100, 10)
		
		for jobLikelihood in np.arange(1e-2, 100e-2, 1e-2):
			# for samples in samplesList:
			processes.append(multiprocessing.Process(target=testRepeatsSeparateThread, args=(i, jobLikelihood, results)))
		
	for process in processes: process.start()
	# for process in processes: process.join()
	

	# legends = list()
	graphs = dict()
	for i in range(len(processes)):
		result = results.get()

		graphName, sample, datapoint = result
		if graphName not in graphs.keys():
			graphs[graphName] = dict()
			
		# print (graphName, sample, datapoint)
		# legends.append(result[0])
		graphs[graphName][sample] = datapoint

	sim.plotting.plotMultiWithErrors("testRepeats", results=graphs) #, ylim=[0, 5])
	