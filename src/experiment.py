from sim import sim
import constants
import variable
import numpy as np
import matplotlib.pyplot as pp
import debug

import multiprocessing
import multiprocessing.pool

import plotting

REPEATS = 8

def singleDelayedJobLocal(accelerated=True):
    constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
    constants.MINIMUM_BATCH = 1
    
    simulation = sim(0, 2, 0, visualise=True)

    constants.JOB_LIKELIHOOD = 0
    # simulation.en[0].createNewJob()
    # simulation.simulateTime(constants.SIM_TIME)
    simulation.simulateTime(constants.PLOT_TD * 10)
    simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=accelerated)
    simulation.simulateTime(0.25)
    
@staticmethod
def singleBatchLocal(accelerated=True):
    constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
    
    simulation = sim(0, 2, 0, visualise=True)

    constants.JOB_LIKELIHOOD = 0
    constants.MINIMUM_BATCH = 2
    # simulation.en[0].createNewJob()
    # simulation.simulateTime(constants.SIM_TIME)
    simulation.simulateTime(constants.PLOT_TD * 10)
    for i in range(constants.MINIMUM_BATCH):
        simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=accelerated)
        simulation.simulateTime(0.1)
    simulation.simulateTime(0.25)
        

@staticmethod
def singleDelayedJobPeer(accelerated=True):
    constants.OFFLOADING_POLICY = constants.PEER_ONLY
    
    simulation = sim(0, 2, 0, visualise=True)

    constants.JOB_LIKELIHOOD = 0
    constants.DEFAULT_TASK_GRAPH = [tasks.EASY]

    simulation.simulateTime(constants.PLOT_TD * 10)
    simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=accelerated)
    simulation.simulateTime(constants.PLOT_TD * 150)
    
@staticmethod
def randomPeerJobs(accelerated=True):
    constants.OFFLOADING_POLICY = constants.PEER_ONLY
    
    simulation = sim(0, 4, 0, visualise=True, hardwareAccelerated=accelerated)

    constants.JOB_LIKELIHOOD = 5e-2
    simulation.simulateTime(constants.PLOT_TD * 100)
    
@staticmethod
def randomLocalJobs(accelerated=True):
    constants.SAMPLE_SIZE = variable.Uniform(5,6)
    constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
    
    simulation = sim(0, 2, 0, visualise=True)

    constants.JOB_LIKELIHOOD = 5e-2
    simulation.simulateTime(constants.PLOT_TD * 100)
  
def totalEnergyJobSize():
    print ("starting experiment")
    debug.enabled = False
    constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
    constants.MINIMUM_BATCH = 1
    constants.JOB_LIKELIHOOD = 0
    
    samplesList = range(1, 100, 10)
    
    results = list()

    for hw in [True, False]:
        graph = list()
        for samples in samplesList:

            thisResult = list()
            constants.SAMPLE_SIZE = variable.Constant(samples)

            for i in range(REPEATS):
                simulation = sim(0, 1, 0, visualise=False)

                simulation.simulateTime(constants.PLOT_TD * 10)
                simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=hw)
                simulation.simulateTime(constants.PLOT_TD * 1500)
                if not simulation.allDone():
                    print ("not all devices done: {}".format(samples))

                thisResult.append(np.sum(simulation.totalDevicesEnergy()))
            
            graph.append((np.average(thisResult), np.std(thisResult)))
        results.append(graph)


    plotting.plotMultiWithErrors(samplesList, results=results)
        
def testRepeatsThread(i, samplesList, resultsQueue):
    # i, samplesList = args
    print ('repeat', i)
    graph = list()
    
    
    for samples in samplesList:

        constants.SAMPLE_SIZE = variable.Constant(1) # samples)

        simulation = sim(0, 1, 0, visualise=False)

        simulation.simulateTime(constants.PLOT_TD * 10)
        simulation.devices[0].createNewJob(simulation.time, hardwareAccelerated=False)
        simulation.simulateTime(constants.PLOT_TD * 1500)
        if not simulation.allDone():
            print ("not all devices done: {}".format(samples))

        graph.append((np.sum(simulation.totalDevicesEnergy()), 0))
            
        # graph.append((np.average(thisResult), np.std(thisResult)))
    # return ("Repeat " + str(i), graph)
    resultsQueue.put(["Repeat " + str(i), graph])
    

def testRepeats():
    print ("starting experiment")
    debug.enabled = False
    constants.OFFLOADING_POLICY = constants.LOCAL_ONLY
    constants.MINIMUM_BATCH = 1
    constants.JOB_LIKELIHOOD = 0
    
    REPEATS = 24

    # results = list()
    constants.SAMPLE_SIZE = variable.Constant(1) # samples)
    samplesList = range(1, 100, 1)

    # pool = multiprocessing.pool.ThreadPool(12)
    processes = list()
    results = multiprocessing.Queue()
    for i in range(REPEATS):
        processes.append(multiprocessing.Process(target=testRepeatsThread, args=(i, samplesList, results)))
    # results = pool.map(testRepeatsThread, [(i, samplesList) for i in range(REPEATS)])
    # pool.close()
    # pool.join()
    for process in processes: process.start()
    for process in processes: process.join()
    

    legends = list()
    graphs = list()
    # for result in results:
    while not results.empty():
        result = results.get()

        legends.append(result[0])
        graphs.append(result[1])

    plotting.plotMultiWithErrors(samplesList, results=graphs, legend=legends, ylim=[0, 5])
        

if __name__ == '__main__':
	# for i in range(1, 100, 10):
	# 	print i, simulation.simulateAll(i, "latency")

	# sim.singleDelayedJobLocal(False)
	# sim.singleDelayedJobLocal(True)
	# sim.singleDelayedJobPeer(False)
	# sim.singleDelayedJobPeer(True)
	# sim.randomPeerJobs(True)
	# sim.randomPeerJobs(False)
    # sim.singleBatchLocal(False)
    
    # totalEnergyJobSize()
    testRepeats()