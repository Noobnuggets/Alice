import numpy as np

def normalize(array):
	return array / array.max()

def linnear_regression(array):
	slope, intercept, r_value, p_value, std_err = stats.linregress(np.arange(len(array)), array)
	return x, intercept + slope*x