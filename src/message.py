from warnings import warn
import constants 

class message:
	size = None
	samples = None

	def __init__(this, size=None, samples=None):

		if samples is None:
			if size is None:
				warn("Must supply size or samples to create message")
			this.size = size
			this.samples = None
		else:
			this.size = samples * constants.SAMPLE_RAW_SIZE.gen()
			this.samples = samples


	# change message from raw to processed
	def process(this):
		if this.samples is None:
			warn("Cannot process message without sample count")
		this.size = this.samples * constants.SAMPLE_PROCESSED_SIZE.gen()