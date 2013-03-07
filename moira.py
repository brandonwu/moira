import requests
import lxml
import logging
from lxml import etree

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

def get_token(username, password):
	"""Issues a login request, returns auth cookiejar.
	
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
	:returns: dictionary keyed with stock symbol
	"""
	url = "http://www.marketwatch.com/game/" + game + \
		"/portfolio/holdings?view=list&partial=True"
	s = requests.Session()
	response = s.get(url, cookies=token).text
	tree = etree.fromstring(response)
	print etree.tostring(tree)
