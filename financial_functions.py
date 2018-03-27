import numpy as np
import matplotlib.pyplot as plt
from utils import *

def weighted_moving_average(prices, period):
	assert type(period) is int, "weighted_moving_average period invalid type: " + str(type(period))

	weights = [i/period for i in range(period)]
	wma = [np.NaN for _ in range(period)]
	for i in range(len(prices)-period):
		wma.append(np.average(prices[i:period+i], weights=weights))
	return np.array(wma)