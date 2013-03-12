"""This example program displays real-time, fractional prices for a selected ticker symbol."""

import argparse

parser = argparse.ArgumentParser(description='demo to display stock prices of a given stock')
parser.add_argument('ticker', help='the ticker symbol to get the price of')
mutex = parser.add_mutually_exclusive_group(required=True)
mutex.add_argument('-u','--username', help='marketwatch.com username (email)')
mutex.add_argument('-t','--cached-token', help='if previously cached login tokens are available, search for them in the default location and use them instead', action='store_true')

parser.add_argument('-p','--password', help='marketwatch.com password (one will be prompted for if not supplied here)')
parser.add_argument('-g','--game', help='name of stock game from marketwatch.com/game/XXXXXX', required=True)
parser.add_argument('-n','--no-continuous', help='do not continuously display the current stock price', action='store_true')

args = parser.parse_args()

import moira
import pickle
import getpass
import datetime
import sys

username = args.username
password = args.password
game = args.game
ticker = args.ticker
outputfmt = '%(time)s %(id)s %(price)s'
timefmt = '{:%Y-%m-%d %H:%M:%S}'

if username:
	if not password:
		password = getpass.getpass()
	token = moira.get_token(username, password)
	with open('/tmp/.moira-token-cache', 'w') as f:
		pickle.dump(token, f)
	print('Token stored to /tmp/.moira-token-cache; on future runs, omit the username and password and use the -t flag for faster startup.')

if args.cached_token:
	with open('/tmp/.moira-token-cache', 'r') as f:
		token = pickle.load(f)

if args.no_continuous:
	r = moira.stock_search(token, game, ticker)
	r['time'] = timefmt.format(r['time'])
	print(outputfmt % r)
else:
	try:
		while 1:
			r = moira.stock_search(token, game, ticker)
			r['time'] = timefmt.format(r['time'])
			print (outputfmt % r)
	except KeyboardInterrupt:
		sys.exit(2)
	except Exception,e:
		pass
