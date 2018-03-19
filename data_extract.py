import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from harmonic_functions import *
from tqdm import tqdm
from trading_functions import *
from scipy import stats

# Import historical data
data = pd.read_csv("Data/coinbaseUSD.csv")

# Drop non-important columns
data.drop('Weighted_Price', axis=1, inplace=True)
data.drop('Volume_(Currency)', axis=1, inplace=True)

data.columns = [["Date", "open", "high", "low", "close", "vol"]]



data = data[["open", "high", "low", "close", "vol"]]

price = data.close.copy()
#price.drop_duplicates(keep=False, inplace=True) #probably useless

#Find relative extrema
price = price.values
labels = ["Gartley", "Butterfly", "Bat", "Crab", "ABCD"]


pattern_performance = {"Bullish Gartley":0,
						"Bullish Butterfly":0,
						"Bullish Bat":0,
						"Bullish Crab":0,
						"Bullish ABCD":0,
						"Bearish Gartley":0,
						"Bearish Butterfly":0,
						"Bearish Bat":0,
						"Bearish Crab":0,
						"Bearish ABCD":0}
patterns_successes = {"Bullish Gartley":[],
						"Bullish Butterfly":[],
						"Bullish Bat":[],
						"Bullish Crab":[],
						"Bullish ABCD":[],
						"Bearish Gartley":[],
						"Bearish Butterfly":[],
						"Bearish Bat":[],
						"Bearish Crab":[],
						"Bearish ABCD":[]}
patterns_failures = {"Bullish Gartley":[],
						"Bullish Butterfly":[],
						"Bullish Bat":[],
						"Bullish Crab":[],
						"Bullish ABCD":[],
						"Bearish Gartley":[],
						"Bearish Butterfly":[],
						"Bearish Bat":[],
						"Bearish Crab":[],
						"Bearish ABCD":[]}

correct_pats = 0
pats = 0
total_closing = 0
slippage = 10/100
equity_pips = [0]
avg_pip_gain = 0
avg_pip_loss = 0
err_allowed = 0#10/100.0
for i in tqdm(range(100, len(price)-100)):
	current_idx, current_pat, start, end = peak_detect2(price[:i])

	XA = current_pat[1] - current_pat[0]
	AB = current_pat[2] - current_pat[1]
	BC = current_pat[3] - current_pat[2]
	CD = current_pat[4] - current_pat[3]

	moves = [XA, AB, BC, CD]

	gart = is_gartley(moves, err_allowed)
	butt = is_butterfly(moves, err_allowed)
	bat = is_bat(moves, err_allowed)
	crab = is_crab(moves, err_allowed)
	abcd = is_abcd(moves, err_allowed)
	pips = 0
	harmonics = np.array([gart, butt, bat, crab, abcd])
	if np.any(harmonics == 1) or np.any(harmonics == -1):
		for j in range(len(harmonics)):
			if harmonics[j] == -1 or harmonics[j] == -1:
				pats += 1
				sense = "Bearish " if harmonics[j] == -1 else "Bullish "
				label = sense + labels[j]

				start = np.array(current_idx).min()
				end = np.array(current_idx).max()

				pips, closing_stat = walk_forward(price[end:], harmonics[j], slippage=3, stop=10)
				
				pips -= slippage #account for slippage
				pattern_performance[label] += pips
				equity_pips.append(equity_pips[-1:][0]+pips)

				if pips > 0:
					avg_pip_gain += pips
				elif pips <= 0:
					avg_pip_loss -= pips
lbl = "Accuracy " + str(100*(correct_pats/pats)) + " %"
print("Total patterns:", pats)
print("Patterns closed on first candle:", total_closing)
print("First candle close:", str(100*(total_closing/pats)) + " %")
print("Average loss:", avg_pip_loss/pats)
print("Average gain:", avg_pip_gain/pats)
print(pattern_performance)
plt.plot(equity_pips)
plt.show()