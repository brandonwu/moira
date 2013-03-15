MOIRA
=====

What is it?
-----------
**MOIRA**, the <b>M</b>OIRA <b>O</b>tto-matic <b>I</b>ntelligent <b>R</b>econniter of <b>A</b>ssets, is an API for the [Marketwatch Virtual Stock Exchange game](http://www.marketwatch.com/game). It provides methods to buy and sell stock, as well as get prices of stock in realtime. This permits one to use quant methods on the Marketwatch VSE - providing a testing ground for algorithms, or merely for the enjoyment of programmatically winning a virtual stock market game.

Who's [Moira](http://fallout.wikia.com/wiki/Moira_Brown)?
------------
The [Megaton](http://fallout.wikia.com/wiki/Megaton) merchant from [Fallout 3](http://en.wikipedia.org/wiki/Fallout_3).

License
-------
This program (and all accompanying code) is licensed by the author under the terms of the [WTFPL](http://www.wtfpl.net/).

What can it do?
---------------
* Login
* Obtain your current holdings in a stock game
* Search for and obtain **real-time**, **fractional-accuracy** stock prices directly from Marketwatch
* Buy, Sell, Short, and Cover stock
* Get portfolio data (cash left, returns, ranking, etc.)

In progress:
------------
* Get transaction and order history
* Simple moving-average-based trader

In the works:
-------------
* Curses-based stock trading interface
* Limit orders and natural-language queries

What's included?
----------------
* The MOIRA module
* An example program, `price_check_sample.py`, that gets you a continuously-updating stock quote on a given stock
 * Sample usage: `python price_check_sample.py -u username@example.com -g game-name ZNGA` on first run, `python price_check_sample.py -tg game-name ZNGA` is sufficient for any subsequent ones
* An example trading program, `trade_sample.py`, that provides a simple keystroke-based trading interface for efficient trades - use a terminal multiplexer like tmux and put this next to the output of `price_check_sample.py`.
 * Sample usage: `python trade_sample.py -u username@example.com -g game-name STOCK-XNAS-ZNGA` on first run, `python trade_sample.py -tg game-name ZNGA` for subsequent times

Documentation
-------------
An HTML, as well as PDF [Epydoc](http://epydoc.sourceforge.net/)-generated API reference is in the `/docs` directory.

<font size=14>[Direct link to PDF documentation](https://github.com/brandonwu/moira/blob/master/docs/api.pdf?raw=true)</font>

Getting started
---------------
This Python module requires the `Requests`, `dateutil`, and `BeautifulSoup` modules (`Requests` for HTTP requests, `dateutil` for server time conversion, and `BeautifulSoup` for parsing pages). Install them from your favorite package manager - for Ubuntu and friends:

```bash
sudo apt-get install python-requests python-dateutil python-beautifulsoup
```

After that, you can try it out in the interpreter.

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

First, you need to get the authentication token - it's necessary for everything.
You'll need your username and password from [Marketwatch](http://www.marketwatch.com/game/) (it'd also be a good idea to join or create a game if you haven't already).

```python
>>> token = moira.get_token('username@example.com', 'password')
2013-03-11 19:32:31,806 INFO: Login success.
```

Try getting your current holdings with the `get_current_holdings()` function. You'll need a part of the game URL: for example, if your game url were `http://www.marketwatch.com/game/foo`, the input you'll need for the `game` parameter would be `foo`.

```python
>>> moira.get_current_holdings(token, 'foo')
{'STOCK-XNAS-GRPN': <moira.Stock instance at 0x279a0e0>, 'STOCK-NYQ-VMW': <moira.Stock instance at 0x279a830>}
```
The `get_current_holdings()` function returns a dictionary of Stock objects. Stock objects have the following attributes:
* id - Unique ID assigned by Marketwatch to each security.
 * Most functions in this module use this ID to refer uniquely to securities (the one exception, of course, is `stock_search()`, which allows you to look up the ID of a stock or ETF).
* ticker - The ticker symbol of the stock.
* security_type - "ExchangeTradedFund" or "Stock"
* current_price - Current price per share, rounded to the cent.
 * It's important to note that this is rounded - use `stock_search()` for fractional prices. Also note that the attribute here is `current_price` to distinguish it from `purchase_price`; the variable referring to current price is simply called `price` when using `stock_search()`.
* shares - Number of shares held.
* purchase_type - "Buy" or "Short"
* returns - Total return on your investment.
* purchase_price - Price at time of purchase. **Not implemented yet.**

So you can use them like this:
```python
>>> stocks = moira.get_current_holdings(token, 'foo')
>>> stocks['STOCK-XNAS-GRPN'].current_price
5.91
```

Or even this:
```python
>>> prices = [stocks[x].current_price for x in stocks]
>>> prices
[5.41, 75.4]
>>> shares = [stocks[x].shares for x in stocks]
>>> shares
[2000.0, 312.0]
>>> values = [x * y for x, y in zip(prices, shares)]
>>> values
[10820.0, 23524.800000000003] #Whoopsie, looks like we got some binary rounding errors.
```

You get the point.

To sell, buy, short, or cover, it's just as simple. However, right now, no checking is done to see if you have enough cash and credit to purchase the stock.

**WARNING:** The server will report that the order was successfully submitted even if you have insufficient funds to make it! The only time the server emits errors is for invalid post parameters in the order request (which is unlikely, since you're using this library.)

Note that the order operation type is capitalized.
```python
>>> moira.order(token, 'foo', 'Sell', 'STOCK-XNAS-GRPN', 100)
2013-03-11 19:32:31,806 INFO: Sell order succeeded. Server said: Your order was successfully submitted
```

Questions, comments, criticisms, enhancements?
----------------------------------------------
Open an issue/make a pull request/etc.
