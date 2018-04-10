import numpy as np
import matplotlib.pyplot as plt
from zigzag import *
from utils import *

def plot_pivots(prices, pivots):
    plt.plot(np.arange(len(prices)), prices, 'k:', alpha=0.5)
    plt.plot(np.arange(len(prices))[pivots != 0], prices[pivots != 0], 'k-')
    plt.scatter(np.arange(len(prices))[pivots == 1], prices[pivots == 1], color='g')
    plt.scatter(np.arange(len(prices))[pivots == -1], prices[pivots == -1], color='r')
    plt.show()
#prices = np.array([1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 4, 5, 7, 8, 10, 12, 10, 9, 7, 6, 5, 4, 5, 6, 7, 8, 9, 10, 12, 13, 12.5, 12.3, 9, 8, 7.5, 7, 6.9])*20

ohlcv = load_ohlcv(candle_period="1H", path="Data/validation.csv")
prices = ohlcv.close.values  

pivots = peak_valley_pivots(prices, 0.1, -0.1)
plot_pivots(prices, pivots)

#plt.plot(prices)
#plt.show()