import requests
import lxml
import logging

#Remove the root logger's default output handlers, otherwise we'll see Requests' logs
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

def login(username, password):
	"""Issues a login request.
	
	:param username: the marketwatch.com username (email)
	:param password: the plaintext marketwatch.com password
	:returns: Requests cookiejar containing authentication token
	"""
	sessionid=requests.get('http://www.marketwatch.com/') #You need to obtain the ASP.NET_SessionId cookie first, which is set by every page except for the login page for some reason.
	sessionid=sessionid.cookies
	userdata={"userName":username,"password":password,"remChk":"on","returnUrl":"/user/login/status","persist":"true"}
	r=requests.post('https://secure.marketwatch.com/user/account/logon', params=userdata, cookies=sessionid) #Pass the SID and user/pass to the account logon endpoint
	logger.debug(sessionid['.ASPXAUTH'])
	check=requests.get('http://www.marketwatch.com/user/login/status',cookies=sessionid) #If the login succeeded, it redirects to http://www.marketwatch.com/my
	if check.url=="http://www.marketwatch.com/my":
		logger.info("Login succeeded.")
	else:
		logger.warn("Authentication failure.")
	return sessionid

def login2(username, password):
	s=requests.Session()
	s.get('http://www.marketwatch.com/')
	userdata={"userName":username,"password":password,"remChk":"on","returnUrl":"/user/login/status","persist":"true"}
	s.post('https://secure.marketwatch.com/user/account/logon', params=userdata)
	if s.get('http://www.marketwatch.com/user/login/status').url=="http://www.marketwatch.com/my":
		logger.info("Login success.")
	else:
		logger.warn("Auth failure.")
	return s.cookies
