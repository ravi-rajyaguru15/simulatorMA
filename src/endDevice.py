import random
import constants

from node import node
from mcu import mcu
from mrf import mrf
from result import result

class endDevice(node):

	def __init__(self, queue, index):
		node.__init__(self, queue, index, nodeType=constants.END_DEVICE)

		self.mcu = mcu()
		self.mrf = mrf()
