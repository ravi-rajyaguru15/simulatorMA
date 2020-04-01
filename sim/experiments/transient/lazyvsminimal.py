import multiprocessing

import sys

from sim import plotting
from sim.experiments.experiment import setupMultithreading, executeMulti
from sim.learning.agent.lazyTableAgent import lazyTableAgent
from sim.learning.agent.minimalTableAgent import minimalTableAgent
from sim.simulations import constants
from sim.simulations.SimpleSimulation import SimpleSimulation
from sim.tasks.tasks import HARD, EASY

numEpisodes = int(1e2)

numDevices = 2
def run(results, finished):
    constants.CENTRALISED_LEARNING = False
    exp = SimpleSimulation(numDevices=numDevices, maxJobs=100, tasks=[HARD])
    exp.setBatterySize(1e0)
    # exp.setBatterySize(1e-5)
    # replace agents in devices
    # for dev in exp.devices:
    #     print(dev.agent, dev.agent.model)
    for agent, device in zip([lazyTableAgent, minimalTableAgent], exp.devices):
        device.agent = agent(systemState=exp.currentSystemState, owner=device, offPolicy=constants.OFF_POLICY)
        device.agent.setDevices(exp.devices)
        print("set agent", agent, agent.__name__, device.agent, device.agent.__name__)
        # device.agent.reset()
        # device.reset()


    print([device.agent.__name__ for device in exp.devices])
    for e in range(int(numEpisodes)):
        exp.simulateEpisode()
        for device in exp.devices:
            print("putting results", device.agent.__name__, device.numJobsDone)
            # results.put(["Agent %s" % device.agent.__name__, e, device.currentTime.current])
            results.put(["Agent %s" % device.agent.__name__, e, device.numJobsDone])

        sys.stdout.write("\rProgress: %.2f%%" % ((e+1)/numEpisodes*100.))

    # for device in exp.devices:
    #     # device.agent.printModel()
    #     device.agent.setProductionMode()

    # for device in exp.devices:
    #     device.agent.printModel()
    finished.put(True)

if __name__ == "__main__":
    setupMultithreading()
    results = multiprocessing.Queue()
    finished = multiprocessing.Queue()

    results = executeMulti([multiprocessing.Process(target=run, args=(results, finished))], results, finished, numResults=numEpisodes * numDevices)




    plotting.plotMulti("Competing Agents", results=results, ylabel="Job #", xlabel="Episode #")  # , save=True)

# <Lazy Agent> Model
# energyRemaining = 0 jobsInQueue = 0 currentConfig = 0  [    0.0015     0.0019     3.7539  ]
# energyRemaining = 0 jobsInQueue = 0 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 0 jobsInQueue = 1 currentConfig = 0  [   -5.8986     0.0019     9.6867  ]
# energyRemaining = 0 jobsInQueue = 1 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 0 jobsInQueue = 2 currentConfig = 0  [   -0.1022     0.0019    16.4031  ]
# energyRemaining = 0 jobsInQueue = 2 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 0 jobsInQueue = 3 currentConfig = 0  [    0.6967    25.0000   -10.7927  ]
# energyRemaining = 0 jobsInQueue = 3 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 0 jobsInQueue = 4 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 0 jobsInQueue = 4 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 0 currentConfig = 0  [    0.0013     0.0019     0.0039  ]
# energyRemaining = 1 jobsInQueue = 0 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 1 currentConfig = 0  [    0.0012     0.0019     0.2711  ]
# energyRemaining = 1 jobsInQueue = 1 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 2 currentConfig = 0  [    0.0010     0.0019     2.4635  ]
# energyRemaining = 1 jobsInQueue = 2 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 3 currentConfig = 0  [   25.0000    25.0000    -0.0001  ]
# energyRemaining = 1 jobsInQueue = 3 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 4 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 4 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 0 currentConfig = 0  [    0.0011     0.0019     0.0039  ]
# energyRemaining = 2 jobsInQueue = 0 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 1 currentConfig = 0  [    0.0011     0.0019     0.2710  ]
# energyRemaining = 2 jobsInQueue = 1 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 2 currentConfig = 0  [    0.0012     0.0019     2.7370  ]
# energyRemaining = 2 jobsInQueue = 2 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 3 currentConfig = 0  [   25.0000    25.0000    -0.0001  ]
# energyRemaining = 2 jobsInQueue = 3 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 4 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 4 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 0 currentConfig = 0  [    0.0013     0.0019     0.0044  ]
# energyRemaining = 3 jobsInQueue = 0 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 1 currentConfig = 0  [    0.0013     0.0019     0.2710  ]
# energyRemaining = 3 jobsInQueue = 1 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 2 currentConfig = 0  [    0.0012     0.0019     2.7371  ]
# energyRemaining = 3 jobsInQueue = 2 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 3 currentConfig = 0  [   25.0000    25.0000    -0.0001  ]
# energyRemaining = 3 jobsInQueue = 3 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 4 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 4 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 0 currentConfig = 0  [    2.4634     0.0045    25.0000  ]
# energyRemaining = 4 jobsInQueue = 0 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 1 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 1 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 2 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 2 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 3 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 3 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 4 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 4 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
#                                                            Offload      Batch      Local
#
# <Minimal Agent> Model
# energyRemaining = 0 jobsInQueue = 0 currentConfig = 0  [  -19.7094  1365.4419  1191.3757  ]
# energyRemaining = 0 jobsInQueue = 0 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 0 jobsInQueue = 1 currentConfig = 0  [  -22.6165  1366.0874  1245.5461  ]
# energyRemaining = 0 jobsInQueue = 1 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 0 jobsInQueue = 2 currentConfig = 0  [  -28.1080  1367.2354  1034.4536  ]
# energyRemaining = 0 jobsInQueue = 2 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 0 jobsInQueue = 3 currentConfig = 0  [  -97.0078    25.0000  1196.7743  ]
# energyRemaining = 0 jobsInQueue = 3 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 0 jobsInQueue = 4 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 0 jobsInQueue = 4 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 0 currentConfig = 0  [   -0.4984  1069.3872  1308.9587  ]
# energyRemaining = 1 jobsInQueue = 0 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 1 currentConfig = 0  [   -0.4992  1073.2962   994.2895  ]
# energyRemaining = 1 jobsInQueue = 1 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 2 currentConfig = 0  [   -0.4993  1076.0746   993.4901  ]
# energyRemaining = 1 jobsInQueue = 2 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 3 currentConfig = 0  [   25.0000    25.0000  1073.0748  ]
# energyRemaining = 1 jobsInQueue = 3 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 4 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 1 jobsInQueue = 4 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 0 currentConfig = 0  [   -0.4984   689.7788   888.0014  ]
# energyRemaining = 2 jobsInQueue = 0 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 1 currentConfig = 0  [   -0.4989   545.2988   692.0423  ]
# energyRemaining = 2 jobsInQueue = 1 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 2 currentConfig = 0  [   -0.4988   564.1127   563.5161  ]
# energyRemaining = 2 jobsInQueue = 2 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 3 currentConfig = 0  [   25.0000    25.0000   561.1131  ]
# energyRemaining = 2 jobsInQueue = 3 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 4 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 2 jobsInQueue = 4 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 0 currentConfig = 0  [   -0.4986   204.9875   437.9247  ]
# energyRemaining = 3 jobsInQueue = 0 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 1 currentConfig = 0  [   -0.4992   210.9499   103.5135  ]
# energyRemaining = 3 jobsInQueue = 1 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 2 currentConfig = 0  [   -0.4993   120.1404   219.4709  ]
# energyRemaining = 3 jobsInQueue = 2 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 3 currentConfig = 0  [   25.0000    25.0000   117.1413  ]
# energyRemaining = 3 jobsInQueue = 3 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 4 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 3 jobsInQueue = 4 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 0 currentConfig = 0  [    2.0123     2.1327     2.1307  ]
# energyRemaining = 4 jobsInQueue = 0 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 1 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 1 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 2 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 2 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 3 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 3 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 4 currentConfig = 0  [   25.0000    25.0000    25.0000  ]
# energyRemaining = 4 jobsInQueue = 4 currentConfig = 1  [   25.0000    25.0000    25.0000  ]
#                                                            Offload      Batch      Local
# waiting for assemble...
#
# Process finished with exit code 0
