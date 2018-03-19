from utils import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from financial_functions import *
def plot(arrays):
	for a in arrays:
		plt.plot(a)
	plt.show()

def long_cnd(hmas):
	return hmas[1] < hmas[2] and hmas[0] > hmas[1]

def short_cnd(hmas):
	return hmas[1] > hmas[2] and hmas[0] < hmas[1]

price_amt = 1000
candle_period = "15min"
ohlcv = load_ohlcv(candle_period=candle_period, price_amt=price_amt)

opens = ohlcv.open.values
highs = ohlcv.high.values
lows = ohlcv.low.values
closes = ohlcv.close.values
vol = ohlcv.volume.values


#These config are all in percent, and optimazible thru genetic algorithms, acc. to Darwin ;)
long_tp = 2
long_sl = 1

short_tp = 2
short_sl = 1


hullma_period = 20
hullma_source = closes

hma = hull_moving_average(hullma_source, hullma_period)

still_open = 0
both_hit = 0
equity = 100
fee = 0.2

# +2 / -2 for hullma comparisson in long_cnd and short_cnd
for i in range(hullma_period+3, len(closes)):
	current_hma = hma[-3+i:i] #last 3 points of hma
	entry_price = closes[i]
	
	if long_cnd(current_hma):
		tp_hit, sl_hit = walk_forward(
			highs=highs[i:],
			lows=lows[i:],
			trade_direction=1,
			entry_price=entry_price,
			take_profit=long_tp,
			stop_loss=long_sl)

		if tp_hit and sl_hit:
			both_hit += 1

		elif tp_hit:
			equity += (long_tp - (fee*2))

		elif sl_hit:
			equity -= (long_sl + (fee*2))

		else:
			still_open += 1

	elif short_cnd(current_hma):
		tp_hit, sl_hit = walk_forward(
			highs=highs[i:],
			lows=lows[i:],
			trade_direction=-1,
			entry_price=entry_price,
			take_profit=short_tp,
			stop_loss=short_sl)

		if tp_hit and sl_hit:
			both_hit += 1

		elif tp_hit:
			equity += (short_tp - (fee*2))

		elif sl_hit:
			equity -= (short_sl + (fee*2))
		
		else:
			still_open += 1
print("Still open #:", still_open)
print("Closed on tp and sl #:", both_hit)
print("Finished equity:", equity)