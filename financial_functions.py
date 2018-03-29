import numpy as np
import matplotlib.pyplot as plt
from utils import *
import pandas as pd
def simple_moving_average(prices, period):
	sma = [np.NaN for _ in range(period)]
	for i in range(period, len(prices)):
		sma.append(np.sum(prices[i-period:i])/period)
	return np.array(sma)

def macd(prices, fast_len, slow_len, signal_len):
	fast_ma = simple_moving_average(prices, period=fast_len)
	slow_ma = simple_moving_average(prices, period=slow_len)

	macd_line = fast_ma - slow_ma
	

	
prices = [1, 2, 3, 4, 5, 4, 5, 6, 7, 8, 10, 11, 13, 12, 10, 9, 10, 8, 9, 10, 13, 15]
sma = simple_moving_average(prices, 5)
plt.plot(prices)
plt.plot(sma)
plt.show()