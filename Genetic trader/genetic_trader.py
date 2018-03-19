import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from harmonic_functions import *
from tqdm import tqdm
from trading_functions import *
from scipy import stats
def load_daily():
	data = pd.read_csv("Data/daily.csv")
	data.drop("time", axis=1, inplace=True)
	column_names = ["timeDate","close","high","low","open","vol"]
	data.columns = [column_names]
	data = data[["open", "high", "low", "close", "vol"]]
	close_price = data.close.copy().values.T[0]
	return close_price

# Import historical data
"""data = pd.read_csv("Data/coinbaseUSD.csv")

# Drop non-important columns
data.drop('Weighted_Price', axis=1, inplace=True)
data.drop('Volume_(Currency)', axis=1, inplace=True)

column_names = ["Date", "open", "high", "low", "close", "vol"]
data.columns = [column_names]



data = data[["open", "high", "low", "close", "vol"]]

close_price = data.close.copy().values.T[0]
"""
close_price = load_daily()
print(close_price)

amount_peaks = 2
order = 1
datapoints_amount = 10
movement_th = 3 #percent
total_bull_movement = 0
total_bear_movement = 0
bear_moves = 0
bull_moves = 0
for i in tqdm(range(datapoints_amount, len(close_price))):
	extremas, price_points, start, end = pattern_analysis(close_price[i:], amount_peaks, order)
	#Check for movement_th
	percent_move = (price_points[1] - price_points[0]) / price_points[0]
	if percent_move > 0:
		total_bull_movement += percent_move
		bull_moves += 1
	elif percent_move < 0:
		total_bear_movement += percent_move
		bear_moves += 1
	else:
		pass
	plt.plot(close_price[i:])
	plt.scatter(extremas, price_points, c="r")
	plt.show()
print("\nBull percent moves:", total_bull_movement/bull_moves)
print("\nBear percent moves:", total_bear_movement/bear_moves)
