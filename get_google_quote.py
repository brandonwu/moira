import requests
import json
import sys
import time

try:
	while 1:
		r = requests.get('http://finance.google.com/finance/info', params={'q': sys.argv[1]})
		j = json.loads(r.text.replace('\n','').replace('/','').replace('[','').replace(']','')) 
		print r.headers['date'], float(j['l_cur'])
#		print time.ctime(), float(j['l_cur'])
		#time.sleep(0.5)
except KeyboardInterrupt:
	sys.exit(0)
except ValueError:
	print r.text
