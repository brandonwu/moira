"""This example program lets you trade a certain stock with single key shortcuts."""

import argparse

parser = argparse.ArgumentParser(description='demo to provide a trading interface')
parser.add_argument('ticker', help='the ticker symbol to trade')
mutex = parser.add_mutually_exclusive_group(required=True)
mutex.add_argument('-u','--username', help='marketwatch.com username (email)')
mutex.add_argument('-t','--cached-token', help='if previously cached login tokens are available, search for them in the default location and use them instead', action='store_true')

parser.add_argument('-p','--password', help='marketwatch.com password (one will be prompted for if not supplied here)')
parser.add_argument('-g','--game', help='name of stock game from marketwatch.com/game/XXXXXX', required=True)
parser.add_argument('-r','--no-colors', help='disable colored output', action='store_true')

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

import sys

try:
    import tty, termios
except ImportError:
    # Probably Windows.
    try:
        import msvcrt
    except ImportError:
        # FIXME what to do on other platforms?
        # Just give up here.
        raise ImportError('error: lp0 on fire\nthis only works on linux and windows due to the method used to get single keypresses.')
    else:
        getch = msvcrt.getch
else:
    def getch():
        """Read a single keypress from stdin and return the resulting character. 
	
	@return: string containing pressed key
        Nothing is echoed to the console. This call will block if a keypress 
        is not already available, but will not wait for Enter to be pressed. 

        If the pressed key was a modifier key, nothing will be detected; if
        it were a special function key, it may return the first character of
        of an escape sequence, leaving additional characters in the buffer.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def _get_shares():
	return raw_input("Number of shares to trade with: ")

shares = _get_shares()

try:
	while 1:
		print("Single-key trading interface.\n"
	      	+ clr.dullgreen + "[d - sell] "
	      	"[f - buy] " + clr.end +
	      	clr.blue + "[j - short] "
	      	"[k - cover]\n" + clr.end +
		clr.peach + "[s - shares] "
		"[q - quit]" + clr.end)
		key = getch()
		try:
			action = {'f': 'Buy',
	 		'd': 'Sell',
	 		'j': 'Short',
	 		'k': 'Cover',
			's': '',
			'q': ''}[key]
			if key == 'q':
				raise KeyboardInterrupt
			if key == 's':
				_get_shares()

			if action:
				print(clr.fuchsia + action + clr.end + ' ' + clr.green + shares + clr.peach + ' @ ' + clr.yellow + '$' + str(moira.stock_search(token, game, ticker.split('-')[2])['price']) + clr.end)
				moira.order(token, game, action, ticker, shares)
		except KeyError:
			print("Invalid key.")
			pass
except KeyboardInterrupt:
	sys.exit(1)
