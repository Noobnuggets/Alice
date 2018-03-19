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

amount_peaks = 5
err_allowed = 10/100
pats = 0

for i in tqdm(range(100, len(price)-100)):
	current_idx, points, start, end = peak_detect2(price[:i], amount_peaks)

	moves = []
	for i in range(len(points)-1):
		move = points[i+1] - points[i]
		moves.append(move)

	pattern = is_pattern(moves, err_allowed, ranges)
	harmonics = np.array([pattern])
	if np.any(harmonics == 1) or np.any(harmonics == -1):
		for j in range(len(harmonics)):
			if harmonics[j] == -1 or harmonics[j] == -1:
				pats += 1

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