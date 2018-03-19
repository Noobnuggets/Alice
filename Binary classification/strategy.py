from utils import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from financial_functions import *

price_amt = 10000000000
candle_period = "1min"
ohlcv = load_ohlcv(candle_period=candle_period, price_amt=price_amt)

opens = ohlcv.open.values
highs = ohlcv.high.values
lows = ohlcv.low.values
closes = ohlcv.close.values
vol = ohlcv.volume.values


#These config are all in percent, and optimazible thru genetic algorithms, acc. to Darwin ;-) 
long_tp = 30
long_sl = -15

short_tp = -30
short_sl = 15


assert long_tp > 0
assert long_sl < 0
assert short_tp < 0
assert short_sl > 0

hullma_period = 160
hullma_source = closes

hma = hull_moving_average(hullma_source, hullma_period)

still_open = 0
both_hit = 0
profit = 0
fee = 0.2
total_trades = 0
long_trades = 0
short_trades = 0
profit_over_trades = []
profit_over_time = []

# +2 / -2 for hullma comparisson in long_cnd and short_cnd
for i in range(hullma_period+3, len(closes)):
	current_hma = hma[-3+i:i] #last 3 points of hma
	entry_price = closes[i]
	
	if long_cnd(current_hma):
		long_trades += 1
		total_trades += 1
		tp_hit, sl_hit = walk_forward_long(
			highs=highs[i:],
			lows=lows[i:],
			entry_price=entry_price,
			take_profit=long_tp,
			stop_loss=long_sl)

		if tp_hit and sl_hit:
			both_hit += 1

		elif tp_hit:
			profit += (long_tp - (fee*2))
			profit_over_trades.append(profit)

		elif sl_hit:
			profit -= (abs(long_sl) + (fee*2))
			profit_over_trades.append(profit)

		else:
			still_open += 1

	elif short_cnd(current_hma):
		short_trades += 1
		total_trades += 1
		tp_hit, sl_hit = walk_forward_short(
			highs=highs[i:],
			lows=lows[i:],
			entry_price=entry_price,
			take_profit=short_tp,
			stop_loss=short_sl)

		if tp_hit and sl_hit:
			both_hit += 1

		elif tp_hit:
			profit += (abs(short_tp) - (fee*2))
			profit_over_trades.append(profit)

		elif sl_hit:
			profit -= (short_sl + (fee*2))
			profit_over_trades.append(profit)
		
		else:
			still_open += 1
	profit_over_time.append(profit)

print("Still open #:", still_open)
print("Closed on tp and sl #:", both_hit)
print("Finished profit:", profit, "%")
print("Total trades:", total_trades)
print("Long trades:", long_trades)
print("Short trades:", short_trades)
plt.plot(profit_over_time)
plt.show()