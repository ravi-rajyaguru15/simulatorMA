import random
import constants

from node import node
from mcu import mcu
from mrf import mrf
from result import result

class endDevice(node):

	def __init__(self, queue):
		node.__init__(self, queue)

		self.mcu = mcu()
		self.mrf = mrf()
