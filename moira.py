import requests
#import lxml
import logging

#Quiet the root logger, otherwise we'll see Requests' logs
logging.getLogger().setLevel(logging.WARN)
#Initialize logging
logger = logging.getLogger('default')
logger.propagate = False
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def login(username,password):
	sessionid=requests.get('http://www.marketwatch.com/') #You need to obtain the ASP.NET_SessionId cookie first, which is set by every page except for the login page for some reason.
	sessionid=sessionid.cookies
	userdata={"userName":username,"password":password,"remChk":"on","returnUrl":"/user/login/status","persist":"true"}
	r=requests.post('https://secure.marketwatch.com/user/account/logon', params=userdata, cookies=sessionid) #Pass the SID and user/pass to the account logon endpoint
	logger.debug(sessionid['.ASPXAUTH'])
	check=requests.get('http://www.marketwatch.com/user/login/status',cookies=sessionid) #If the login succeeded, it redirects to http://www.marketwatch.com/my
	if check.url=="http://www.marketwatch.com/my":
		logger.info("Login succeeded.")
	else:
		logger.info("Authentication failure.")
