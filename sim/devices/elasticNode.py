import sim.debug
import sim.simulations.constants
from sim.devices.components.fpga import fpga
from sim.devices.components.mcu import mcu
from sim.devices.components.mrf import mrf
from sim.devices.node import node


class elasticNode(node):
	def __repr__(self):
		return "<Elastic Node {0}>".format(self.index)

	# message = None
	mcu = None
	mrf = None
	fpga = None

	def __init__(self, inputClock, platform, queue, index, episodeFinished, currentSystemState, offloadingDecisionClass, agentClass, alwaysHardwareAccelerate):
		node.__init__(self, inputClock, platform, index, currentSystemState=currentSystemState, components = None, episodeFinished=episodeFinished, offloadingDecisionClass=offloadingDecisionClass, agentClass=agentClass, alwaysHardwareAccelerate=alwaysHardwareAccelerate)
		
		self.mcu = mcu(self)
		self.mrf = mrf(self)
		self.fpga = fpga(self)

		self.setComponents([self.mcu, self.fpga, self.mrf])

	def getCurrentConfiguration(self):
		if self.hasFpga():
			config = self.fpga.currentConfig
			if config is not None:
				return config.identifier
			else:
				return 0
		else:
			return 0

	
	# def processingEnergy(self, duration):
	# 	return self.mcu.idleEnergy(duration) + self.mrf.idleEnergy(duration) + self.fpga.activeEnergy(duration)

	# def reconfigurationEnergy(self, duration):
	# 	return self.mcu.idleEnergy(duration) + self.mrf.idleEnergy(duration) + self.fpga.reconfigurationEnergy(duration)

	# def processingTime(self, job):
	# 	print ("ONLY FPGA processing")
	# 	return self.fpga.processingTime(job.samples)

	def mcuToFpgaLatency(self, datasize):
		latency = datasize / self.platform.MCU_FPGA_COMMUNICATION_SPEED.gen() + self.platform.MCU_MW_OVERHEAD_LATENCY.gen()
		sim.debug.out ("offloading latency: {}".format(latency))
		return latency

	# def mcuToFpgaEnergy(self, time):
	# 	mcuEnergy = self.mcu.activeEnergy(time)
	# 	fpgaEnergy = self.fpga.activeEnergy(time)
	# 	return mcuEnergy + fpgaEnergy

	# def process(self, task):
	# 	print 'simple task for now'
		
		# res = result(latency=self.mcu.processingTime(task.samples), energy=self.mcu.activeEnergy(self.mcu.processingTime(task.samples)))
		
	# def process(this, accelerated):
	# 	res = None
	# 	if accelerated:
	# 		# overhead for mcu-fpga communication
	# 		time = this.mcuToFpgaLatency()
	# 		res = result(latency=time, energy=this.mcuToFpgaEnergy(time))
	# 		# processing 
	# 		res += this.fpga.process(this.message.samples)
	# 	else:
	# 		res = result(latency=this.mcu.processingTime(this.message.samples), energy=this.mcu.activeEnergy(this.mcu.processingTime(this.message.samples)))

	# 	this.message.process()

	# 	return res


	# def localProcessMcu(this, samples):
	# 	# process locally on mcu
	# 	this.ed.message = message(samples=samples)
	# 	res = this.ed.process() 
	# 	# print 'local:\t\t\t\t\t', res

	# 	return res


	# def localProcessFpga(this, samples):
	# 	# process locally on fpga
	# 	this.ed.message = message(samples=samples)
	# 	res = this.ed.process() 
	# 	# print 'local:\t\t\t\t\t', res

	# 	return res