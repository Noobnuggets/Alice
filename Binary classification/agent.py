import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from random import uniform, randint, choice
from financial_functions import *
from utils import *
class Trader():
	def __init__(self, starting_USD=100000, fee=0.1, conf=None):
		self.USD = starting_USD
		self.fee = fee

		#Metrics
		self.profit = 0

		self.profit_over_time = []
		self.profit_over_trades = []

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

		if self.conf is None:
			self.conf = {
			"ma_period":randint(3, 500),
			"long_tp":uniform(1, 20),
			"short_tp":uniform(-20, -1),
			"long_sl":uniform(-20, -1),
			"short_sl":uniform(1, 20),
			"ma_source":choice(ma_sources),
			"ma_func":choice(ma_types),
			}

		#Trading
		self.long_position = False
		self.short_position = False
		self.entry_price = None
		
		#Unittest
		assert type(self.USD) is int or type(self.USD) is float, "starting_USD is invalid: " + str(type(self.USD))
		assert self.conf["long_tp"] > 0, "long_tp is invalid: " + str(self.conf["long_tp"])
		assert self.conf["long_sl"] < 0, "long_sl is invalid: " + str(self.conf["long_sl"])
		assert self.conf["short_tp"] < 0, "short_tp is invalid: " + str(self.conf["short_tp"])
		assert self.conf["short_sl"] > 0, "short_sl is invalid: " + str(self.conf["short_sl"])
		assert type(self.conf["ma_period"]) is int, "ma_period is invalid type: " + str(type(self.conf["ma_period"]))
		assert self.conf["ma_period"] > 3 and self.conf["ma_period"] < 1000, "ma_period is invalid: " + str(self.conf["ma_period"])

	def long_cnd(self, ma):
		assert len(ma) == 3, "long_cnd ma invalid len: " + str(len(ma))
		return ma[1] < ma[2] and ma[0] > ma[1]

	def short_cnd(self, ma):
		assert len(ma) == 3, "long_cnd ma invalid len: " + str(len(ma))
		return ma[1] > ma[2] and ma[0] < ma[1]

	def event(self, current_i, current_price, current_low, current_high):
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
			self.handle_long(current_high, current_low)

		elif self.short_position:
			self.handle_short(current_high, current_low)


	def handle_long(self, current_high, current_low):
		percent_move_high = ((current_high - self.entry_price) / self.entry_price) * 100
		percent_move_low = ((current_low - self.entry_price) / self.entry_price) * 100

		sl_hit = percent_move_low <= self.conf["long_sl"]
		tp_hit = percent_move_high > self.conf["long_tp"]

		#Close long with stop-loss
		if sl_hit and not tp_hit:
			self.long_position = False

			#Trades
			self.profit -= abs(self.conf["long_sl"]) + (self.fee * 2)

			#metrics
			self.loosing_trades += 1
			self.loosing_long_trades += 1
			self.profit_over_trades.append(self.profit)

		#Close long with take-profit
		elif tp_hit and not sl_hit:
			self.long_position = False

			#Trades
			self.profit += self.conf["long_tp"] - (self.fee * 2)

			#Metrics
			self.winning_trades += 1
			self.winning_long_trades += 1
			self.profit_over_trades.append(self.profit)

		elif tp_hit and sl_hit:
			self.long_position = False
			self.both_hit += 1

	def handle_short(self, current_high, current_low):
		percent_move_high = ((current_high - self.entry_price) / self.entry_price) * 100
		percent_move_low = ((current_low - self.entry_price) / self.entry_price) * 100

		sl_hit = percent_move_high >= self.conf["short_sl"]
		tp_hit = percent_move_low < self.conf["short_tp"]

		#Close short with stop-loss
		if sl_hit and not tp_hit:
			self.short_position = False

			#Trades
			self.profit -= self.conf["short_sl"] + (self.fee * 2)

			#metrics
			self.loosing_trades += 1
			self.loosing_short_trades += 1
			self.profit_over_trades.append(self.profit)

		#Close short with take-profit
		elif tp_hit and not sl_hit:
			self.short_position = False

			#Trades
			self.profit += abs(self.conf["short_tp"]) - (self.fee * 2)

			#Metrics
			self.winning_trades += 1
			self.winning_short_trades += 1
			self.profit_over_trades.append(self.profit)

		elif tp_hit and sl_hit:
			self.short_position = False
			self.both_hit += 1
			
	def reset(self):
		self.profit = 0

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

		self.short_position = False
		self.long_position = False