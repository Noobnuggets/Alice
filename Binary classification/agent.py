import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from random import uniform, randint, choice
from financial_functions import *
from utils import *

def delta_y(points):
	deltas = []
	for i in range(int(round(len(points)/2))):pass

class Trader():
	def __init__(self, starting_USD=100000, fee=0.2, conf=None, margin=3, margin_fee = 0.1):
		self.USD = starting_USD
		self.fee = fee

		#Metrics
		self.profit = 0

		self.profit_over_time = [0]
		self.profit_over_trades = [0]

		self.long_trades = 0
		self.short_trades = 0
		self.total_trades = 0

		self.winning_trades = 0
		self.loosing_trades = 0

		self.both_hit = 0

		self.winning_short_trades = 0
		self.winning_long_trades = 0

		self.loosing_short_trades = 0
		self.loosing_long_trades = 0




		#conf stuff
		ma_sources = ["open", "close", "low", "high", "hl2", "hlc3", "ohlc4"]
		ma_types = [hull_moving_average, weighted_moving_average, simple_moving_average, exponential_moving_average]
		self.conf = conf
		
		max_range = 20
		min_range = 3
		if self.conf is None:
			self.conf = {
			"ma_period":randint(3, 50),
			"long_tp":uniform(min_range, max_range),
			"short_tp":uniform(-max_range, -min_range),
			"long_sl":uniform(-max_range, -min_range),
			"short_sl":uniform(min_range, max_range),
			"ma_source":choice(ma_sources),
			"ma_func":choice(ma_types),
			}

		#Trading
		self.long_position = False
		self.short_position = False
		self.entry_price = None

		self.profit_ratio = 0
		self.margin = margin
		self.margin_fee = margin_fee
		
		#Unittest
		assert type(self.USD) is int or type(self.USD) is float, "starting_USD is invalid: " + str(type(self.USD))
		assert self.conf["long_tp"] > 0, "long_tp is invalid: " + str(self.conf["long_tp"])
		assert self.conf["long_sl"] < 0, "long_sl is invalid: " + str(self.conf["long_sl"])
		assert self.conf["short_tp"] < 0, "short_tp is invalid: " + str(self.conf["short_tp"])
		assert self.conf["short_sl"] > 0, "short_sl is invalid: " + str(self.conf["short_sl"])
		assert type(self.conf["ma_period"]) is int, "ma_period is invalid type: " + str(type(self.conf["ma_period"]))
		assert self.conf["ma_period"] >= 3 and self.conf["ma_period"] <= 50, "ma_period is invalid: " + str(self.conf["ma_period"])

	def long_cnd(self, ma):
		assert len(ma) == 3, "long_cnd ma invalid len: " + str(len(ma))
		return ma[1] < ma[2] and ma[0] > ma[1]

	def short_cnd(self, ma):
		assert len(ma) == 3, "long_cnd ma invalid len: " + str(len(ma))
		return ma[1] > ma[2] and ma[0] < ma[1]

	def event(self, current_i, current_price, current_low, current_high): 
		assert (self.long_position and not self.short_position) or (self.short_position and not self.long_position) or (not self.short_position and not self.long_position), "More positions.."
		#Metrics
		self.profit_over_time.append(self.profit)


		current_ma = self.conf["ma"][-3+current_i:current_i] #three lasts point, used for slope

		#If not already in a position, check for potential positions
		if not self.long_position and not self.short_position:
			if self.long_cnd(current_ma):
				self.long_trades += 1
				self.total_trades += 1
				self.long_position = True
				self.entry_price = current_price

			elif self.short_cnd(current_ma):
				self.short_trades += 1
				self.total_trades += 1
				self.short_position = True
				self.entry_price = current_price
		
		elif self.long_position:
			self.handle_long(current_high, current_low, current_price, current_i)

		elif self.short_position:
			self.handle_short(current_high, current_low, current_price, current_i)


	def handle_long(self, current_high, current_low, current_close, current_i):
		percent_move_high = ((current_high - self.entry_price) / self.entry_price) * 100
		percent_move_low = ((current_low - self.entry_price) / self.entry_price) * 100

		sl_hit = percent_move_low <= self.conf["long_sl"]
		tp_hit = percent_move_high > self.conf["long_tp"]

		current_ma = self.conf["ma"][-3+current_i:current_i] #three lasts point, used for slope

		#Close long with stop-loss
		if sl_hit and not tp_hit:
			self.long_position = False

			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2)#positive
			trade = abs(self.conf["long_sl"] * self.margin)

			#unittest
			assert fees > 0, "fees are negative!"
			assert trade > 0, "trade are negative!"
			self.profit -= trade + fees

			#metrics
			self.loosing_trades += 1
			self.loosing_long_trades += 1
			self.profit_over_trades.append(self.profit)


		#Close long with take-profit
		elif tp_hit and not sl_hit:
			self.long_position = False

			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = self.conf["long_tp"] * self.margin  #positive

			#unittest
			assert fees > 0, "fees are negative!"
			assert trade > 0, "trade are negative!"

			self.profit += trade - fees

			#Metrics
			self.winning_trades += 1
			self.winning_long_trades += 1
			self.profit_over_trades.append(self.profit)


		elif tp_hit and sl_hit:
			self.long_position = False
			self.both_hit += 1


		#Close due to short cnd
		elif short_cnd(current_ma):
			self.long_position = False

			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = (((current_close - self.entry_price) / self.entry_price) * 100) * self.margin

			#unittest
			assert fees > 0, "fees are negative!"

			#If it is a loss
			if trade < 0:
				self.profit -= abs(trade) + fees

				#Metrics
				self.loosing_trades += 1
				self.loosing_long_trades += 1
				self.profit_over_trades.append(self.profit)
			
			#if it is a win
			elif trade > 0:
				#Also win after fees are applied
				if trade - fees > 0:
					self.profit += trade - fees

					#Metrics
					self.winning_trades += 1
					self.winning_long_trades += 1
					self.profit_over_trades.append(self.profit)

				#otherwise
				else:
					self.profit += trade - fees #negative

					#Metrics
					self.loosing_trades += 1
					self.loosing_long_trades += 1
					self.profit_over_trades.append(self.profit)

	def handle_short(self, current_high, current_low, current_close, current_i):
		percent_move_high = ((current_high - self.entry_price) / self.entry_price) * 100
		percent_move_low = ((current_low - self.entry_price) / self.entry_price) * 100

		sl_hit = percent_move_high >= self.conf["short_sl"]
		tp_hit = percent_move_low < self.conf["short_tp"]

		current_ma = self.conf["ma"][-3+current_i:current_i] #three lasts point, used for slope
		
		#Close short with stop-loss
		if sl_hit and not tp_hit:
			self.short_position = False

			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = abs(self.conf["short_sl"] * self.margin) #positive

			#unittest
			assert fees > 0, "fees are negative!"
			assert trade > 0, "trade are negative!"

			self.profit -= trade + fees

			#metrics
			self.loosing_trades += 1
			self.loosing_short_trades += 1
			self.profit_over_trades.append(self.profit)

		#Close short with take-profit
		elif tp_hit and not sl_hit:
			self.short_position = False

			#Trades 
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = abs(self.conf["short_tp"] * self.margin) #positive

			#unittest
			assert fees > 0, "fees are negative!"
			assert trade > 0, "trade are negative!"

			self.profit +=  trade - fees

			#Metrics
			self.winning_trades += 1
			self.winning_short_trades += 1
			self.profit_over_trades.append(self.profit)

		elif tp_hit and sl_hit:
			self.short_position = False
			self.both_hit += 1
		
		
		#Close due to long cnd
		elif long_cnd(current_ma):
			self.short_position = False

			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = (((current_close - self.entry_price) / self.entry_price) * 100) * self.margin

			#unittest
			assert fees > 0, "fees are negative!"

			#If it is a loss
			if trade > 0:
				self.profit -= abs(trade) + fees

				#Metrics
				self.loosing_trades += 1
				self.loosing_short_trades += 1
				self.profit_over_trades.append(self.profit)
			
			#if it is a win
			elif trade < 0:
				#Also win after fees are applied
				if trade + fees < 0:
					self.profit += abs(trade) - fees

					#Metrics
					self.winning_trades += 1
					self.winning_short_trades += 1
					self.profit_over_trades.append(self.profit)

				#otherwise
				else:
					self.profit -= trade + fees #negative

					#Metrics
					self.loosing_trades += 1
					self.loosing_short_trades += 1
					self.profit_over_trades.append(self.profit)


	def reset(self):

		#Metrics
		self.profit = 0

		self.profit_over_time = [0]
		self.profit_over_trades = [0]

		self.long_trades = 0
		self.short_trades = 0
		self.total_trades = 0

		self.winning_trades = 0
		self.loosing_trades = 0

		self.both_hit = 0

		self.winning_short_trades = 0
		self.winning_long_trades = 0

		self.loosing_short_trades = 0
		self.loosing_long_trades = 0

		#Trading
		self.long_position = False
		self.short_position = False
		self.entry_price = None

		self.profit_ratio = 0

	
	def fitness_func(self):
		win_res = abs((self.winning_short_trades * self.conf["short_tp"])) + (self.winning_long_trades * self.conf["long_tp"])
		lose_res = (self.loosing_short_trades * self.conf["short_sl"]) + abs((self.loosing_long_trades * self.conf["long_sl"]))

		if lose_res == 0:
			lose_res = 1
		
		self.fitness = win_res / lose_res
