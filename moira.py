import requests
import logging
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
#class Portfolio(timeupdated, stocks, cash, leverage, net_worth,
#		 purchasing_power, starting_cash, return_amt):
def blah():
	"""Stores portfolio data.

	:param timeupdated: server time from headers
	:param stock: dict of stock objects keyed on id
	:param cash: current cash remaining
	:param leverage: current amount left under borrowing limit
	:param net_worth: sum of assets and liabilities
	:param purchasing_power: amount (credit + cash) left to purchase
	:param starting_cash: cash amount provided at game start
	:param return_amt: amount of return obtained from trading
	"""

#TODO: implement stock class
#class Stock(token, id, ticker, security_type, current_price, shares, purchase_type,
#	     purchase_price, returns):
	"""Stores stock data.

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

	def get_purchase_price(token, id):
		#parse transactions page here for purchase price; alternatively,
		#calculate it from the provided ROI
	
	self.purchase_price = get_purchase_price(id)

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

def get_portfolio(token, game):
	"""Downloads and parses current portfolio, returns dict.

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
	trs = soup.find_all('tr')
	trs.pop(0)
	security_type = [ x['data-insttype'] for x in trs ]
	id = [ x['data-symbol'] for x in trs ]
	ticker = [ x['data-ticker'] for x in trs ]
	price = [ x['data-price'] for x in trs ]
	shares = [ x['data-shares'] for x in trs ]
	purchase_type = [ x['data-type'] for x in trs ]
	#TODO: get ROI by parsing inner text for TDs...need extra logic
	#to determine which stock goes with which return data
	print(time, security_type, id, ticker, price, shares, purchase_type)
	#assemble stock objects
	#stock objects are stored in a dict keyed by the stock id
	for x in trs:
		s = Stock()
		s.id = x['data-symbol']
		s.ticker = x['data-ticker']
		s.security_type = x['data-insttype']
		s.purchase_type = x['data-type']
		s.shares = x['data-shares']
		stock_dict[x] = s
	p = Portfolio()
	p.time = time
	p.stocks = stock_dict
