import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from analytic_wfm import peakdetect
import peakutils
from utils import *

def peak_detect(price, amount_peaks=2, order=10):
	maximums = list(argrelextrema(price, np.greater, order=order)[0])
	minimums = list(argrelextrema(price, np.less, order=order)[0])

	extremas = maximums + minimums + [len(price)-1]
	extremas.sort()
	extremas = extremas[-amount_peaks:]
	
	

	start = min(extremas)
	end = max(extremas)

	price_points = price[extremas]

	return np.array(extremas), np.array(price_points), start, end

def pattern_analysis(prices, amount_peaks, order):
	extremas, price_points, start, end = peak_detect(prices, amount_peaks, order)
	return np.array(extremas), np.array(price_points), start, end