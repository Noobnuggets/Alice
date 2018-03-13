import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from harmonic_functions import *
from tqdm import tqdm
from trading_functions import *

# Import historical data
data = pd.read_csv("Data/Bitstamp_1m_USDBTC.csv")

# Drop non-important columns
data.drop('Weighted_Price', axis=1, inplace=True)
data.drop('Volume_(Currency)', axis=1, inplace=True)

data.columns = [["Date", "open", "high", "low", "close", "vol"]]



data = data[["open", "high", "low", "close", "vol"]]

price = data.close.copy()
price.drop_duplicates(keep=False, inplace=True) #probably useless

#Find relative extrema

err_allowed = 10/100.0

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
pnl = []
correct_pats = 0
pats = 0
total_closing = 0
slippage = 1/100
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

	harmonics = np.array([gart, butt, bat, crab, abcd])
	if np.any(harmonics == 1) or np.any(harmonics == -1):
		for j in range(len(harmonics)):
			if harmonics[j] == -1 or harmonics[j] == -1:
				pats += 1
				sense = "Bearish " if harmonics[j] == -1 else "Bullish "
				label = sense + labels[j]

				start = np.array(current_idx).min()
				end = np.array(current_idx).max()

				pips, closing_stat = walk_forward(price[end:], harmonics[j], slippage=0, stop=15)
				total_closing += closing_stat
				pips -= slippage #account for slippage
				pnl = np.append(pnl, pips)

				pattern_performance[label] += pips

				print(data["vol"][j][])
				cumpips = pnl.cumsum()

				if pips > 0:
					correct_pats += 1
lbl = "Accuracy " + str(100*(correct_pats/pats)) + " %"
print("Total patterns:", pats)
print("Patterns closed on first candle:", total_closing)
print("First candle close:", str(100*(total_closing/pats)) + " %")
print(pattern_performance)
plt.plot(cumpips, label=lbl)
plt.legend()
plt.show()