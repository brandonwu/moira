"""Nukaquant is a library for technical and quant analysis of stock data. It is intended to be used with its companion Marketwatch API library, moira."""

import math

class MovingAverage:
	"""Calculates the moving average for a data stream.

	@param period: The number of samples to average; if the actual
		       number of samples provided is less than this,
		       the mavg attribute will be the simple average.
	@ivar mavg: The moving average of the data added with L{add_value}.
	"""
	def __init__(self, period=30):
		self.period = period
		self.data = []
		self.mavg = None

	def _recalculate_average(self):
		self.mavg = math.fsum(self.data) / len(self.data)

	def _flush_old_data(self):
		if len(self.data) > self.period:
			del self.data[0:len(self.data)-self.period]

	def add_value(self, value):
		"""Adds a sample to the moving average calculation window.

		@param value: The numerical value of the sample to add.
		"""
		self.data.append(value)
		self._recalculate_average()
		self._flush_old_data()

class Bollinger:
	"""Calculates the high and low Bollinger bands for a data stream.

	@param mavg_obj: A MovingAverage object containing the data.
	"""
	def __init__(self, mavg_obj, num_sd=2):
		self.period = mavg_obj.period
		self.num_sd = num_sd
		self.mavg_obj = mavg_obj

	def _recalculate_sd(self):
		sum_x2 = math.fsum([x ** 2 for x in self.mavg_obj.data])
		n = len(self.mavg_obj.data)
		mean = self.mavg_obj.mavg
		self.sd = math.sqrt((sum_x2 / n) - (mean ** 2)) 

	def get_bollinger(self):
		"""Returns the high and low Bollinger bands.

		@returns: Tuple(lowband, midband, highband)
		"""
		self._recalculate_sd()
		mean = self.mavg_obj.mavg
		sd = self.sd
		mult = self.num_sd
		bollinger = (mean - (mult * sd),
			     mean,
			     mean + (mult * sd))
		return bollinger
