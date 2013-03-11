import requests
import logging
import re #Regex to clean up parsed out numbers
import json #Send/buy requests are JSON-encoded
from bs4 import BeautifulSoup

#Remove the root logger's default output handler
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
#Initialize logging
logger = logging.getLogger('default')
logger.propagate = False
logger.setLevel(logging.INFO)
#Initialize console output handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
#Initialize log formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

#Class it up so we'll be able to do portfolio.stock['EXCHANGETRADEDFUND-XASQ-IXJ'].price
#TODO: implement portfolio class
class Portfolio():
	"""Stores portfolio data.

	:param time: server time from headers
	:param stock: dict of stock objects keyed on id
	:param cash: current cash remaining
	:param leverage: current amount left under borrowing limit
	:param net_worth: sum of assets and liabilities
	:param purchasing_power: amount (credit + cash) left to purchase
	:param starting_cash: cash amount provided at game start
	:param return_amt: amount of return obtained from trading
	"""
	def __init__(self, time, stocks, cash, leverage, net_worth,
		     purchasing_power, starting_cash, return_amt):
		self.time = time
		self.stocks = stocks
		self.cash = cash
		self.leverage = leverage
		self.net_worth = net_worth
		self.purchasing_power = purchasing_power
		self.starting_cash = starting_cash
		self.return_amt = return_amt

#TODO: implement purchase_price handling in Stock class
class Stock():
	"""Stores portfolio data for a single stock.

	:param token: auth token (used to get purchase price and ROI)
	:param id: unique id assigned by marketwatch to each security
	:param ticker: stock symbol
	:param security_type: "ExchangeTradedFund" or "Stock"
	:param current_price: current price per share
	:param shares: number of shares held
	:param purchase_type: "Buy" or "Short"
	:param return: ROI
	x:param purchase_price: price at time of purchase
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

	:param ticker: the ticker symbol of the security
	:param order_time: the time the order was issued
	:param trans_time: the time the order was executed
	:param trans_type: "Buy", "Short", "Sell", or "Cover"
	:param trans_amt: number of shares sold/purchased
	:param exec_price: price of security at time of order
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
	"""Issues a login request, returns auth cookiejar. Nom nom nom!

	:param username: the marketwatch.com username (email)
	:param password: the plaintext marketwatch.com password
	:returns: Requests cookiejar containing authentication token
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
	if s.get('http://www.marketwatch.com/user/login/status').url == \
		"http://www.marketwatch.com/my":
		logger.info("Login success.")
	else:
		logger.warn("Auth failure.")
	return s.cookies

def get_stocksdict(token, game):
	"""Fetches and parses current holdings, returns dict.

	:param token: cookiejar returned by a call to get_token()
	:param game: the name of the game (marketwatch.com/game/XXXXXXX)
	:returns: portfolio object
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
			  float(x['data-shares']), x['data-type'],
			  float(re.sub("\r\n\t*", "", y.contents[0]). \
			  replace(',','')) #TODO: incl purchase price
			 )
		stock_dict[x['data-symbol']] = o
	#p = Portfolio()
	#access the data in the stock dict returned like so:
	#stock_dict['EXCHANGETRADEDFUND-XASQ-IXJ'].current_price
	return stock_dict

def get_transaction_history(token, game):
	"""Downloads and parses past transactions, returns Trans object

	:param token: cookiejar returned by get_token
	:param game: game name, marketwatch.com/game/XXXXXXX
	:returns: Trans object
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
	"""Searches for stock price and ID of a given ticker

	:param token: cookiejar returned by get_token
	:param ticker: ticker symbol
	:returns: {'price': current price, 'id': Fuid, 'time': server time}
	"""
	s = requests.Session()
	search_url = 'http://www.marketwatch.com/game/msj-2013/trade?week=1'
	postdata = {'search': ticker, 'view': 'grid', 'partial': 'true'}
	soup = BeautifulSoup(s.post(search_url, data=postdata,
				    cookies=token).text)
	try:
		price = float(soup.find('div',{'class': 'chip'})['data-price'])
	except KeyError:
		logger.error('Stock data query failed, check token and retry.')
		return 1
	symbol = soup.find('div',{'class': 'chip'})['data-symbol']
	dict = {'price': price, 'symbol': symbol}
	return dict

def get_portfolio(token, game):
	print "hi"

def sell(token, game, id, amt):
	"""Sells a stock
Post [{"Fuid":"EXCHANGETRADEDFUND-XASQ-IXJ","Shares":"100","Type":"Sell"}]
http://www.marketwatch.com/game/msj-2013/trade/submitorder?week=1
response:{"succeeded":true,"message":"Your order was submitted successfully"}
"""
	s = requests.Session()
	order_url = 'http://www.marketwatch.com/game/msj-2013/trade/' \
		    'submitorder?week=1'
	postdata = JSONEncoder().encode({'Fuid': id,
					 'Shares': str(amt),
					 'Type': 'Sell'})
	resp = BeautifulSoup(s.post(order_url, data=postdata,
				    cookies=token).text)
	
