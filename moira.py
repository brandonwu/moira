"""MOIRA, the MOIRA Otto-matic Intelligent Reconniter of Assets, is an API for the Marketwatch Virtual Stock Exchange game.

Code is available on U{Github<http://github.com/brandonwu/moira>}.
"""
__docformat__ = "epytext en"

import requests
import logging
import re #Regex to clean up parsed out numbers
import json #Send/buy requests are JSON-encoded
from datetime import datetime
from dateutil import tz
from bs4 import BeautifulSoup

if __name__ == "__main__":
	"""TODO: Put unit tests here or something.
	@exclude:
	"""
	print("This is a Python module, to be imported into your own programs.\n"
	      'Use `import moira` in the interactive interpreter or your scripts.')

#Initialize logging
logger = logging.getLogger('default')
"""@exclude:"""
logger.propagate = False
logger.setLevel(logging.DEBUG)
#Initialize console output handler
ch = logging.StreamHandler()
fh = logging.FileHandler('moira.log', mode='w')
"""@exclude:"""
ch.setLevel(logging.INFO)
fh.setLevel(logging.DEBUG)
#Initialize log formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
"""@exclude:"""
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

#Timezone conversion
from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/New_York')

#Class it up so we'll be able to do portfolio.stock['EXCHANGETRADEDFUND-XASQ-IXJ'].price
#TODO: implement portfolio class
class Portfolio():
	"""Stores portfolio data.

	@param time: Last updated time (server time from HTTP headers).
	@param cash: Amount of I{cash} (not purchasing power!) remaining.
	@param leverage: Amount available to borrow.
	@param net_worth: Sum of assets and liabilities.
	@param purchasing_power: Amount (credit + cash) available to buy.
	@param starting_cash: Cash amount provided at game start.
	@param return_amt: Dollar amount of returns over L{starting_cash}.
	"""
	def __init__(self, time, cash, leverage, net_worth, purchasing_power,
		     starting_cash, return_amt, rank):
		self.time = time
		self.cash = cash
		self.leverage = leverage
		self.net_worth = net_worth
		self.purchasing_power = purchasing_power
		self.starting_cash = starting_cash
		self.return_amt = return_amt
		self.rank = rank

#TODO: implement purchase_price handling in Stock class
class Stock():
	"""Stores portfolio data for a single stock.

	@param id: Unique ID assigned by Marketwatch to each security.
	@param ticker: The ticker symbol of the stock.
	@param security_type: "ExchangeTradedFund" or "Stock"
	@param current_price: Current price per share, I{rounded to the cent}.
	@param shares: Number of shares held.
	@param purchase_type: "Buy" or "Short"
	@param returns: Total return on your investment.
	@see See the warnings at L{get_current_holdings} about price rounding.
	"""
	def __init__(self, id, ticker, security_type, current_price, shares,
		     purchase_type, returns): #purchase_price
		self.id = id
		self.ticker = ticker
		self.security_type = security_type
		self.current_price = current_price
		self.shares = shares
		self.purchase_type = purchase_type
#		self.purchase_price = purchase_price
		self.returns = returns

class Trans():
	"""Stores transaction data for a single transaction.

	@param ticker: The ticker symbol of the security.
	@param order_time: The time the order was issued.
	@param trans_time: The time the order was executed.
	@param trans_type: "Buy", "Short", "Sell", or "Cover"
	@param trans_amt: Number of shares sold/purchased.
	@param exec_price: Price of security at time of order.
	"""
	def __init__(self, ticker, order_time, trans_time, trans_type,
		     trans_amt, exec_price):
		self.ticker = ticker
		self.order_time = order_time
		self.trans_time = trans_time
		self.trans_type = trans_type
		self.trans_amt = trans_amt
		self.exec_price = exec_price

def get_token(username, password):
	"""Issues a login request. The token returned by this function
	is required for all methods in this module.

	@param username: The marketwatch.com username (email).
	@param password: The plaintext marketwatch.com password.
	@return: Requests cookiejar containing authentication token.
	@note: It's unknown what the expiry time for this token is - it is
	       set to expire at end of session. It may be apt to request
	       a new token daily, while the market is closed.
	"""
	userdata = {
		"userName": username,
		"password": password,
		"remChk": "on",
		"returnUrl": "/user/login/status",
		"persist": "true"
	}
	s = requests.Session()
	s.get('http://www.marketwatch.com/')
	s.post('https://secure.marketwatch.com/user/account/logon',
		params=userdata)
	#TODO: Turn this into something that checks the cookiejar for .ASPXAUTH instead; this takes WAY too long.
	if s.get('http://www.marketwatch.com/user/login/status').url == \
		"http://www.marketwatch.com/my":
		logger.info("Login success.")
	else:
		logger.warn("Auth failure.")
	return s.cookies

def get_current_holdings(token, game):
	"""Fetches and parses current holdings.

	@param token: Cookiejar returned by a call to L{get_token}.
	@param game: The X{name} of the game (marketwatch.com/game/I{XXXXXXX}).
	@return: L{Stock} data.
	@rtype: Dict of L{Stock} objects, keyed by X{id}
	@warning: The stock price returned by a call to L{get_current_holdings}
	    is rounded to the nearest cent! This results in inaccuracies if you
	    calculate things based on this number --- don't. Use L{stock_search}
	    instead. Interestingly, Marketwatch itself never reports the full-
	    precision stock price anywhere except in HTML attributes.
	"""
	url = ("http://www.marketwatch.com/game/%s/portfolio/holdings"
	"?view=list&partial=True") % game
	p = requests.Session()
	r = p.get(url, cookies=token)
	time = r.headers['date']
	response = r.text
	soup = BeautifulSoup(response)
	#the trs in portf. page have stock data atributes in the tag
	trs = soup.find_all('tr')
	trs.pop(0) #remove table header row
	#get tds for current ROI per stock
	tds = soup.find_all('td', {'class': 'marketgain'})
	#TODO: get purchase_price by parsing orders page
	#assemble stock objects
	#stock objects are stored in a dict keyed by the stock id
	stock_dict = {}
	for x,y in zip(trs, tds):
		o = Stock(x['data-symbol'], x['data-ticker'],
			  x['data-insttype'], float(x['data-price']),
			  int(float(x['data-shares'])), x['data-type'],
			  float(re.sub("\r\n\t*", "", y.contents[0]). \
			  replace(',','')) #TODO: incl purchase price
			 )
		stock_dict[x['data-symbol']] = o
	#p = Portfolio()
	#access the data in the stock dict returned like so:
	#stock_dict['EXCHANGETRADEDFUND-XASQ-IXJ'].current_price
	return stock_dict

def get_transaction_history(token, game):
	"""DOES NOT FUNCTION YET: Downloads and parses the list of past transactions.

	@param token: Cookiejar returned by L{get_token}.
	@param game: The X{name} of the game (marketwatch.com/game/I{XXXXXXX}).
	@return: A dict of all past transactions.
	@rtype: Dict of L{Trans} objects, keyed on an index (1, 2...).
	"""
	orders_url = ("http://www.marketwatch.com/game/msj-2013/portfolio/"
		      "transactionhistory?sort=TransactionDate&descending="
		      "True&partial=true&index=%s")
	s = requests.Session()
	soup = BeautifulSoup(s.get(orders_url, cookies=token).text)
	total = int(soup.find('a',{'class':'fakebutton'})['href'].
		split('&')[1].split('=')[1])
	if total >= 10:
		whole = int(str(total)[0:-1])*10
	else:
		whole = 0
	tail = total - whole
	for i in range(0, whole, 10):
		r = s.get(orders_url % i, token)
		ordersoup = BeautifulSoup(r)

def stock_search(token, game, ticker):
	"""Queries Marketwatch for stock price and ID of a given ticker symbol.

	@note: You must have joined a game in order to use this function.
	@param token: Cookiejar returned by L{get_token}.
	@param game: Game name (marketwatch.com/game/I{XXXXXXX}).
	@param ticker: Ticker symbol of stock to query.
	@return: Current stock price, stock id, and server time.
	@rtype: Dict {'price':float,
		'id':str,
		'time':I{datetime} object in EST}.
	"""
	s = requests.Session()
	search_url = 'http://www.marketwatch.com/game/%s/trade?week=1' % game
	postdata = {'search': ticker, 'view': 'grid', 'partial': 'true'}
	r = s.post(search_url, data=postdata, cookies=token)
	if not r.status_code == 200:
		logger.error('Server returned HTTP %s; probably rate-limiting.' \
			     % r.status_code)
		return 1
	soup = BeautifulSoup(r.text)
	time = datetime.strptime(r.headers['date'],'%a, %d %b %Y %H:%M:%S %Z')
	time = time.replace(tzinfo=from_zone).astimezone(to_zone)
	try:
		price = float(soup.find('div',{'class': 'chip'})['data-price'])
		symbol = soup.find('div',{'class': 'chip'})['data-symbol']
		dict = {'price': price, 'id': symbol, 'time': time}
		return dict
	except TypeError:
		logger.error('Invalid game or Marketwatch rate-limiting.')
		logger.debug(r.headers)
		logger.debug(r.text)
		pass
	except KeyError:
		logger.error('Invalid stock ticker symbol provided, or '
			     'Marketwatch rate-limiting.')
		logger.debug(r.headers)
		logger.debug(r.text)
		pass
	except Exception,e:
		logger.debug(r.headers)
		logger.debug(r.text)
		pass

def get_portfolio_data(token, game):
	"""Grabs portfolio data.

	@param token: Cookiejar returned by L{get_token}.
	@param game: Game name (marketwatch.com/game/I{XXXXXXX})
	@return: Portfolio data dictionary
	@rtype: Dict with net_worth, overall_return_amount, overall_return_percent,
		daily_return_percent, purchasing_power, cash_left, cash_borrowed,
		short_reserve, rank, and time (last updated).
	@note: I probably won't be making this return a L{Portfolio} object; it seems
	       slightly redundant.
	"""
	s = requests.Session()
	portfolio_url = "http://www.marketwatch.com/game/%s/portfolio" % game
	d = s.get(portfolio_url, cookies=token)
	r = BeautifulSoup(d.text)
	time = datetime.strptime(d.headers['date'],'%a, %d %b %Y %H:%M:%S %Z')
	time = time.replace(tzinfo=from_zone).astimezone(to_zone)
	rank = r.find('p', {'class': 'rank'}).contents[0]
	if rank != '--':
		rank = int(rank)
	data = r.find_all('span', {'class': 'data'})
	data = [ float(re.sub('[^-\d\.]', '', x.contents[0])) for x in data ]
	data_keys = ['net_worth', 'overall_return_amount', 'overall_return_percent',
		     'daily_return_percent', 'purchasing_power', 'cash_left',
		     'cash_borrowed', 'short_reserve']
	data = dict(zip(data_keys, data))
	data.update({'rank': rank, 'time': time})
	return data

def order(token, game, type, id, amt):
	"""Initiates a buy, sell, short, or cover order.

	@warning: If you have insufficient funds, the server will still
		  respond that the order succeeded! Check the order and
		  transaction list to make sure the order actually went
		  through.
	@param token: Cookiejar returned by L{get_token}.
	@param game: Game name (marketwatch.com/game/I{XXXXXXX})
	@param id: Security ID (not the ticker symbol).
		   Obtain from L{stock_search}
	@param amt: Order amount.
	@param type: Type of order - 'Sell', 'Buy', 'Short', or 'Cover'.
	@return: Returns integer - 0 if success, nonzero if failure.
	@rtype: integer
	"""
	s = requests.Session()
	order_url = 'http://www.marketwatch.com/game/msj-2013/trade/' \
		    'submitorder?week=1'
	postdata = '['+json.dumps({'Fuid': id, 'Shares': str(amt), \
				   'Type': type})+']'
	headers = {'X-Requested-With': 'XMLHttpRequest',
		   'Content-Type': 'application/json',
		   'charset': 'UTF-8'}
	resp = json.loads(s.post(order_url, data=postdata, cookies=token,
				 headers=headers).text)
	if resp['succeeded'] == True:
		logger.info('Order may have succeeded. Server said: %s' \
			    % resp['message'])
		return True, resp['message']
	else:
		logger.error('Order failed. Server said: %s' \
			     % resp['message'])
		return False, resp['message']
