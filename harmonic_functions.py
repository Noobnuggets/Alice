import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from analytic_wfm import peakdetect

def peak_detect2(price, order=1):
	extremas = []
	for i in range(len(price)-2, 1, -1):
		prev_value = price[i-1]
		next_value = price[i+1]
		this_value = price[i]
		#Max point found
		if prev_value < this_value and next_value < this_value:
			extremas.append(i)

		#Min point
		elif prev_value > this_value and next_value > this_value:
			extremas.append(i)

		if len(extremas) == 5:
			break

	extremas.append(len(price)-1)

	extremas.sort()
	

	start = min(extremas)
	end = max(extremas)

	current_pat = price[extremas]

	return extremas, current_pat, start, end

def is_gartley(moves, err_allowed):
	XA = moves[0]
	AB = moves[1]
	BC = moves[2]
	CD = moves[3]

	AB_range = np.array([0.618 - err_allowed, 0.618 + err_allowed])*abs(XA)
	BC_range = np.array([0.382 - err_allowed, 0.886 + err_allowed])*abs(AB)
	CD_range = np.array([1.27 - err_allowed, 1.618 + err_allowed])*abs(BC)
	#Check for up-down-up-down
	#Bullish gartley
	if XA > 0 and AB < 0 and BC > 0 and CD < 0:

		if AB_range[0] < abs(AB) < AB_range[1] and BC_range[0] < abs(BC) < BC_range[1] and CD_range[0] < abs(CD) < CD_range[1]:
			return 1
		else:
			return np.NaN

	#Bearish gartley
	elif XA < 0 and AB > 0 and BC < 0 and CD > 0:
		if AB_range[0] < abs(AB) < AB_range[1] and BC_range[0] < abs(BC) < BC_range[1] and CD_range[0] < abs(CD) < CD_range[1]:
			return -1
		else:
			return np.NaN
	else:
		return np.NaN

def is_butterfly(moves, err_allowed):
	XA = moves[0]
	AB = moves[1]
	BC = moves[2]
	CD = moves[3]

	AB_range = np.array([0.786 - err_allowed, 0.786 + err_allowed])*abs(XA)
	BC_range = np.array([0.382 - err_allowed, 0.886 + err_allowed])*abs(AB)
	CD_range = np.array([1.618 - err_allowed, 2.618 + err_allowed])*abs(BC)
	#Check for up-down-up-down
	
	#Bullish
	if XA > 0 and AB < 0 and BC > 0 and CD < 0:

		if AB_range[0] < abs(AB) < AB_range[1] and BC_range[0] < abs(BC) < BC_range[1] and CD_range[0] < abs(CD) < CD_range[1]:
			return 1
		else:
			return np.NaN

	#Bearish
	elif XA < 0 and AB > 0 and BC < 0 and CD > 0:
		if AB_range[0] < abs(AB) < AB_range[1] and BC_range[0] < abs(BC) < BC_range[1] and CD_range[0] < abs(CD) < CD_range[1]:
			return -1
		else:
			return np.NaN
	else:
		return np.NaN

def is_bat(moves, err_allowed):
	XA = moves[0]
	AB = moves[1]
	BC = moves[2]
	CD = moves[3]

	AB_range = np.array([0.382 - err_allowed, 0.5 + err_allowed])*abs(XA)
	BC_range = np.array([0.382 - err_allowed, 0.886 + err_allowed])*abs(AB)
	CD_range = np.array([1.618 - err_allowed, 2.618 + err_allowed])*abs(BC)
	#Check for up-down-up-down
	
	#Bullish
	if XA > 0 and AB < 0 and BC > 0 and CD < 0:

		if AB_range[0] < abs(AB) < AB_range[1] and BC_range[0] < abs(BC) < BC_range[1] and CD_range[0] < abs(CD) < CD_range[1]:
			return 1
		else:
			return np.NaN

	#Bearish
	elif XA < 0 and AB > 0 and BC < 0 and CD > 0:
		if AB_range[0] < abs(AB) < AB_range[1] and BC_range[0] < abs(BC) < BC_range[1] and CD_range[0] < abs(CD) < CD_range[1]:
			return -1
		else:
			return np.NaN
	else:
		return np.NaN

def is_crab(moves, err_allowed):
	XA = moves[0]
	AB = moves[1]
	BC = moves[2]
	CD = moves[3]

	AB_range = np.array([0.382 - err_allowed, 0.618 + err_allowed])*abs(XA)
	BC_range = np.array([0.382 - err_allowed, 0.886 + err_allowed])*abs(AB)
	CD_range = np.array([2.24 - err_allowed, 3.618 + err_allowed])*abs(BC)
	#Check for up-down-up-down
	
	#Bullish
	if XA > 0 and AB < 0 and BC > 0 and CD < 0:

		if AB_range[0] < abs(AB) < AB_range[1] and BC_range[0] < abs(BC) < BC_range[1] and CD_range[0] < abs(CD) < CD_range[1]:
			return 1
		else:
			return np.NaN

	#Bearish
	elif XA < 0 and AB > 0 and BC < 0 and CD > 0:
		if AB_range[0] < abs(AB) < AB_range[1] and BC_range[0] < abs(BC) < BC_range[1] and CD_range[0] < abs(CD) < CD_range[1]:
			return -1
		else:
			return np.NaN
	else:
		return np.NaN

def is_ABCD(moves, err_allowed):
	#XA is not included
	AB = moves[1]
	BC = moves[2]
	CD = moves[3]

	BC_range = np.array([0.618 - err_allowed, 0.786 + err_allowed])*abs(AB)
	CD_range = np.array([1.27 - err_allowed, 1.618 + err_allowed])*abs(BC)

	#Bullish
	if AB < 0 and BC > 0 and CD < 0:
		if BC_range[0] < abs(BC) < BC_range[1] and CD_range[0] < abs(CD) < CD_range[1]:
			return 1
		else:
			return np.NaN

	#Bearish
	if AB > 0 and BC < 0 and CD > 0:
		if BC_range[0] < abs(BC) < BC_range[1] and CD_range[0] < abs(CD) < CD_range[1]:
			return 1
		else:
			return np.NaN
	else:
		return np.NaN