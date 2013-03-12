MOIRA
=====

What is it?
-----------
**MOIRA**, the <b>M</b>OIRA <b>O</b>tto-matic <b>I</b>ntelligent <b>R</b>econniter of <b>A</b>ssets, is an API for the [Marketwatch Virtual Stock Exchange game](http://www.marketwatch.com/game). It provides methods to buy and sell stock, as well as get prices of stock in realtime. This permits one to use quant methods on the Marketwatch VSE - providing a testing ground for algorithms, or merely for the enjoyment of programmatically winning a virtual stock market game.

License
-------
This program (and all accompanying code) is licensed by the author under the terms of the [WTFPL](http://www.wtfpl.net/).

What can it do?
---------------
* Login
* Obtain your current holdings in a stock game
* Search for and obtain **real-time**, **fractional-accuracy** stock prices directly from Marketwatch
* Sell stock

In progress:
------------
* Get portfolio data (cash left, returns, ranking, etc.)
* Get transaction and order history
* Buy stock

In the works:
-------------
* Curses-based stock trading interface
* Limit orders and natural-language queries

Getting started
---------------
This Python module requires the `Requests`, `dateutil`, and `BeautifulSoup` modules. Install them from your favorite package manager - for Ubuntu and friends:

```bash
sudo apt-get install python-requests python-dateutil python-beautifulsoup
```

After that, you can try it out in the interpreter (example scripts coming soon).

```bash
ubuntu@bigmac ~ $ cd moira
ubuntu@bigmac ~/moira $ python
```

```python
Python 2.7.3 (default, Aug  1 2012, 05:14:39)
[GCC 4.6.3] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import moira
```

First, you need to get the authentication token -- it's necessary for everything.

```python
>>> token = moira.get_token('username@example.com', 'password')
2013-03-11 19:32:31,806 INFO: Login success.
```

