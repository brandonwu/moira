"""Nukaquant is a library for technical and quant analysis of stock data. It is intended to be used with its companion Marketwatch API library, moira."""

import math

class MovingAverage:
	"""Calculates the moving average for a data stream.

	@param period: The number of samples to average; if the actual
		       number of samples provided is less than this,
		       the mavg attribute will be the simple average.
	@ivar data: List of data inputted
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
		self.sum_x2 = math.fsum([x ** 2 for x in self.mavg_obj.data])
		self.n = len(self.mavg_obj.data)
		self.mean = self.mavg_obj.mavg
		#Take the absolute value before square rooting because
		#sometimes there's binary rounding error and it ends up
		#negative
		self.sd = math.sqrt(math.fabs((self.sum_x2 / self.n) - (self.mean ** 2))) 

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

class LocalExtrema:
	"""Attempts to find price pivot points over a given interval
	in a stream of data.

	@param auto_period: If true, this dynamically increases the
			    period to fit price cycles.
	@param max_period: The max value that L{auto_period} will increase
			   the period to.
	@param period: Size of window for pivot point determination.
	@param dec_threshold: Amount of change to happen before the window
			      is decreased. Values of 0.4-0.7 will work for
			      volatile stocks.			
	@ivar data: Current window of data inputted
	@ivar high: Predicted current high point
	@ivar low: Predicted current low point
	@ivar slope: Current price direction
	"""
	def __init__(self, auto_period=False, period=20, max_period=100, dec_threshold=0.05):
		self.period = period
		self.initialperiod = period
		self.auto_period = auto_period
		self.max_period = max_period
		self.dec_threshold = dec_threshold
		self.data = []
		self.high = 0
		self.low = 0
		self.ssto = 0

	def _recalculate_extrema(self):
		self.phigh = self.high
		self.high = max(self.data)
		self._highcount = self.data.count(self.high)
		self.plow = self.low
		self.low = min(self.data)
		self._lowcount = self.data.count(self.low)

	def _auto_period(self):
		if self.high == self.low and not len(self.data) < self.period:
			self.high = self.phigh
			self.low = self.plow
			self.period += 1
		if self.period >= self.max_period:
			self.period = self.max_period
		self.ssto = sum([abs(x) for x in self._derivatives])
		if self.ssto > self.dec_threshold:
			self.period -= 1

	def _recalculate_derivatives(self):
		datasub = self.data[1:-1]
		data = self.data[0:-2]
		self._derivatives = [x - y for x,y in zip(data,datasub)]

	def _flush_old_data(self):
		if len(self.data) > self.period:
			del self.data[0:len(self.data)-self.period]

	def add_value(self, value):
		self.data.append(value)
		self._flush_old_data()
		self._recalculate_derivatives()
		self._recalculate_extrema()
		if self.auto_period:
			self._auto_period()

	def clear_data(self):
		self.data = []
		self.period = self.initialperiod

class OrderQueue:
	"""Trying this out. Don't use it yet.

	@ivar nextaction: When the next order is scheduled.
	"""
	def __init__(self):
		self.orderdata = []

	def add_order(self, position, type, amount, price):
		"""Adds an order to the OrderQueue.

		@param position: When to execute the order ('high' or 'low')
		@param type: 'Buy', 'Sell', 'Short', or 'Cover'.
		@param amount: Number of securities to order.
		"""
		check = self._check_order(position, type, amount)
		if check[0]:
			self.orderdata.append({'position': position,
					       'type': type,
					       'amount': amount,
					       'price': price})
			self.nextaction = position
			self.pendingorders = True
			return True
		else:
			return False, check[1]

	def _check_order(self, position, type, amount):
		"""Checks the order you're adding against the next-executing order in the queue.

		@return: True if the order is valid and False if the order is not
		"""
		currentamount = amount
		currenttype = type
		if not len(self.orderdata):
			if not (currenttype == 'Buy' or currenttype == 'Short'):
				return False, "First order must be Buy or Short"
			else:
				return True, True

		checkorder = self.orderdata[-1]
		checktype = checkorder['type']
		checkamount = checkorder['amount']
		if currenttype == checkorder['type']:
			return False, "Can't have multiples of the same order sequentially"
		else:
			if currenttype == 'Sell' and checktype != 'Buy':
				return False, "Can't sell without having bought"
			if currenttype == 'Cover' and checktype != 'Short':
				return False, "Can't cover without having shorted"
			if (currenttype == 'Buy' or currenttype == 'Short') and \
			   checktype != 'Cover' and checktype != 'Sell':
				return False, "Can't buy or short without having" \
				"covered or sold"
			if currenttype == 'Sell' or currenttype == 'Cover':
				if checkamount == currentamount:
					return True, True
				else:
					return False, "Amount sold/covered must be" \
					" equal to amount bought/shorted"
			else:
				return True, True

	def get_latest_order(self, position):
		if len(self.orderdata):
			for x in (self.orderdata):
				if x['position'] == position:
					self.orderdata.remove(x)
					return x
					break
		else:
			return None

	def clear_orders(self):
		self.orderdata = []
