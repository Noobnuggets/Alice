from utils import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
def plot(arrays):
	for a in arrays:
		plt.plot(a)
	plt.show()
prices_total = 10000
ohlcv = load_ohlcv(ohlcv_period="1H", price_amt=prices_total)
