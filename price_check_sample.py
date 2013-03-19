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
parser.add_argument('-r','--no-colors', help='disable colored output', action='store_true')
parser.add_argument('-l','--use-local-time', help='display system time instead of server time', action='store_true')

args = parser.parse_args()

import moira
import pickle
import getpass
import datetime
import time
import sys

class clr:
    black = '\033[30m'
    red = '\033[31m'
    dullgreen = '\033[32m'
    dullyellow = '\033[33m'
    brown = '\033[34m'
    peach = '\033[35m'
    pink = '\033[36m'
    peach2 = '\033[37m'
    dullred = '\033[1;31m'
    green = '\033[1;32m'
    yellow = '\033[1;33m'
    blue = '\033[1;34m'
    fuchsia = '\033[1;35m'
    goldenrod = '\033[1;36m'
    white = '\033[1;37m'
    end = '\033[0m'
    def disable(self):
		self.black = ''
		self.red = ''
		self.dullgreen = ''
		self.dullyellow = ''
		self.brown = ''
		self.peach = ''
		self.pink = ''
		self.peach2 = ''
		self.dullred = ''
		self.green = ''
		self.yellow = ''
		self.blue = ''
		self.fucshia = ''
		self.goldenrod = ''
		self.white = ''
		self.end = ''

username = args.username
password = args.password
game = args.game
ticker = args.ticker
outputfmt = clr.pink + '%(time)s' + clr.blue + ' %(id)s' + clr.end + clr.peach + ' $%(price)s' + clr.end
timefmt = '{:%Y-%m-%d %H:%M:' + clr.dullyellow + '%S}'

if args.no_colors:
	clr.disable()

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
	if not args.use_local_time:
		r['time'] = timefmt.format(r['time'])
	else:
		r['time'] = time.ctime()
	print(outputfmt % r)
else:
	try:
		while 1:
			r = moira.stock_search(token, game, ticker)
			tick = time.mktime(r['time'].timetuple())
			if tick % 2:
				sym = u'\u25cf'
			else:
				sym = u'\u25cb'
			r['time'] = clr.dullgreen + sym + clr.end + ' ' + clr.pink + timefmt.format(r['time'])
			if args.use_local_time:
				r['time'] = time.ctime()
			print('\r\033[K' + outputfmt % r)
			time.sleep(.1)
	except KeyboardInterrupt:
		sys.exit(2)
	except Exception,e:
		pass
