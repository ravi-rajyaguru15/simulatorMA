import constants
from node import node
from mcu import mcu
from mrf import mrf
from fpga import fpga
from result import result

class elasticNode(node):
	# message = None
	mcu = None
	mrf = None
	fpga = None

	def __init__(self, queue, index, alwaysHardwareAccelerate):
		
		self.mcu = mcu()
		self.mrf = mrf()
		self.fpga = fpga()

		node.__init__(self, queue, index, nodeType=constants.ELASTIC_NODE, components = [self.mcu, self.fpga, self.mrf], alwaysHardwareAccelerate=alwaysHardwareAccelerate)


	# def processingEnergy(self, duration):
	# 	return self.mcu.idleEnergy(duration) + self.mrf.idleEnergy(duration) + self.fpga.activeEnergy(duration)

	# def reconfigurationEnergy(self, duration):
	# 	return self.mcu.idleEnergy(duration) + self.mrf.idleEnergy(duration) + self.fpga.reconfigurationEnergy(duration)

	# def processingTime(self, job):
	# 	print ("ONLY FPGA processing")
	# 	return self.fpga.processingTime(job.samples)

	def mcuToFpgaLatency(self, datasize):
		latency = datasize / 1024. / constants.MCU_FPGA_COMMUNICATION_SPEED.gen() + constants.MCU_MW_OVERHEAD_LATENCY.gen()
		print ("offloading latency:", latency)
		return latency

	def mcuToFpgaEnergy(self, time):
		mcuEnergy = self.mcu.activeEnergy(time)
		fpgaEnergy = self.fpga.activeEnergy(time)
		return mcuEnergy + fpgaEnergy

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