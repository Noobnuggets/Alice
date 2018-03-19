import numpy as np
from scipy.stats import linregress
import pandas as pd

def normalize(array):
	return array / array.max()

def linnear_regression(array):
	x = np.arange(len(array))-1
	slope, intercept, r_value, p_value, std_err = linregress(x, array)
	return slope, intercept, r_value, p_value, std_err, x

def resample_OHLCV(ohlcv_df, column_names):
	data = ohlcv_df.copy()

	ohlc_dict = {                                                                                                             
    str(column_names[0]):'first',                                                                                                    
    str(column_names[1]):'max',                                                                                                       
    str(column_names[2]):'min',                                                                                                        
    str(column_names[3]): 'last',                                                                                                    
    str(column_names[4]): 'sum'                                                                                                        
	}

	data.resample('D', how=ohlc_dict, closed='left', label='left')
	return data