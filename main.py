import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from harmonic_functions import *
from tqdm import tqdm
from trading_functions import *

# Import historical data
data = pd.read_csv("Data/testPrices_big.csv")

# Drop non-important columns
data.drop('Weighted_Price', axis=1, inplace=True)
data.drop('Volume_(Currency)', axis=1, inplace=True)

data.columns = [["Date", "open", "high", "low", "close", "vol"]]

data.drop_duplicates(keep=False, inplace=True) #probably useless

data = data[["open", "high", "low", "close", "vol"]]

price = data.close.copy()


#Find relative extrema

err_allowed = 10/100.0

price = price.values
labels = ["Gartley", "Butterfly", "Bat", "Crab"]

pnl = []
correct_pats = 0
pats = 0
total_closing = 0
for i in tqdm(range(100, len(price))):
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

	harmonics = np.array([gart, butt, bat, crab])
	if np.any(harmonics == 1) or np.any(harmonics == -1):
		for j in range(len(harmonics)):
			if harmonics[j] == -1 or harmonics[j] == -1:
				pats += 1
				sense = "Bearish " if harmonics[j] == -1 else "Bullish "
				label = sense + labels[j] + " Found"

				start = np.array(current_idx).min()
				end = np.array(current_idx).max()

				pips, closing_stat = walk_forward(price[end:], harmonics[j], slippage=0, stop=50)
				total_closing += closing_stat
				pnl = np.append(pnl, pips)
				cumpips = pnl.cumsum()

				if pips > 0:
					correct_pats += 1
lbl = "Accuracy " + str(100*(correct_pats/pats)) + " %"
print("Total patterns:", pats)
print("Patterns closed on first candle:", total_closing)
print("First candle close:", str(100*(total_closing/pats)) + " %")
plt.plot(cumpips, label=lbl)
plt.legend()
plt.show()