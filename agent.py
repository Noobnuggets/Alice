import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from random import uniform, randint, choice
from financial_functions import *
from utils import *

class Trader():
	def __init__(self, max_lookback, starting_usd=100000, fee=0.2, conf=None, margin=3.3, margin_fee = 0.015):
		self.usd = starting_usd
		self.usd_over_time = []


		self.percent_per_trade = 5
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
		sources = ["open", "close", "low", "high", "hl2", "hlc3", "ohlc4"]
		self.conf = conf
		
		max_range = 20
		min_range = 3

		max_sl = 3
		min_sl = 1
		

		if self.conf is None:
			self.conf = {
			"fast_ma_period":randint(2, max_lookback-1),
			"slow_ma_period":randint(2, max_lookback),
			"signal_period":randint(2, 13),

			"long_tp":randint(min_range, max_range),
			"short_tp":randint(-max_range, -min_range),
			"long_sl":randint(-max_sl, -min_sl),
			"short_sl":randint(min_sl, max_sl),

			"source":choice(sources),
			}

		#Trading
		self.long_position = False
		self.short_position = False
		self.entry_price = None

		self.profit_ratio = 0
		self.margin = margin
		self.margin_fee = margin_fee

		self.fitness = 0
		
		#Unittest

		assert self.conf["long_tp"] > 0, "long_tp is invalid: " + str(self.conf["long_tp"])
		assert self.conf["long_sl"] < 0, "long_sl is invalid: " + str(self.conf["long_sl"])
		assert self.conf["short_tp"] < 0, "short_tp is invalid: " + str(self.conf["short_tp"])
		assert self.conf["short_sl"] > 0, "short_sl is invalid: " + str(self.conf["short_sl"])

	def long_cnd(self, macd, signal):
		assert len(macd) == 2, "long_cnd macd invalid len: " + str(len(macd))
		assert len(signal) == 2, "long_cnd signal invalid len: " + str(len(signal))
		#return (signal[0] > macd[0] and signal[1] < macd[1]) and (macd[0] < 0 and macd[1] > 0)
		return macd[0] < 0 and macd[1] > 0

	def short_cnd(self, macd, signal):
		assert len(macd) == 2, "long_cnd macd invalid len: " + str(len(macd))
		assert len(signal) == 2, "long_cnd signal invalid len: " + str(len(signal))
		#return (signal[0] < macd[0] and signal[1] > macd[1]) and (macd[0] > 0 and macd[1] < 0)
		return macd[0] > 0 and macd[1] < 0
	

	def event(self, current_i, current_price, current_low, current_high): 
		assert (self.long_position and not self.short_position) or (self.short_position and not self.long_position) or (not self.short_position and not self.long_position), "More positions.."
		#Metrics
		self.profit_over_time.append(self.profit)
		self.usd_over_time.append(self.usd)


		current_macd = self.conf["macd"][-2+current_i:current_i]
		current_signal = self.conf["signal"][-2+current_i:current_i]
		#If not already in a position, check for potential positions
		if not self.long_position and not self.short_position:
			if self.long_cnd(current_macd, current_signal):
				self.long_trades += 1
				self.total_trades += 1
				self.long_position = True
				self.entry_price = current_price

			elif self.short_cnd(current_macd, current_signal):
				self.short_trades += 1
				self.total_trades += 1
				self.short_position = True
				self.entry_price = current_price
		
		elif self.long_position:
			self.handle_long(current_high, current_low, current_price, current_i)

		elif self.short_position:
			self.handle_short(current_high, current_low, current_price, current_i)


	def handle_long(self, current_high, current_low, current_close, current_i):
		assert self.long_position
		percent_move_high = ((current_high - self.entry_price) / self.entry_price) * 100
		percent_move_low = ((current_low - self.entry_price) / self.entry_price) * 100

		sl_hit = percent_move_low <= self.conf["long_sl"]
		tp_hit = percent_move_high > self.conf["long_tp"]

		current_macd = self.conf["macd"][-2+current_i:current_i]
		current_signal = self.conf["signal"][-2+current_i:current_i]

		#Close long with stop-loss
		if sl_hit and not tp_hit:
			self.long_position = False

			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2)#positive
			trade = abs(self.conf["long_sl"] * self.margin)

			#unittest
			assert fees >= 0, "fees are negative!"
			assert trade >= 0, "trade are negative!"
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
			assert fees >= 0, "fees are negative!"
			assert trade >= 0, "trade are negative!"

			self.profit += trade - fees

			#Metrics
			self.winning_trades += 1
			self.winning_long_trades += 1
			self.profit_over_trades.append(self.profit)


		elif tp_hit and sl_hit:
			self.long_position = False
			self.both_hit += 1


		#Close due to short cnd
		elif self.short_cnd(current_macd, current_signal):
			self.long_position = False
			self.short_trades = True
			self.short_trades += 1
			self.total_trades += 1

			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = (((current_close - self.entry_price) / self.entry_price) * 100) * self.margin
			self.entry_price = current_close
			#unittest
			assert fees >= 0, "fees are negative!"

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
		assert self.short_position
		percent_move_high = ((current_high - self.entry_price) / self.entry_price) * 100
		percent_move_low = ((current_low - self.entry_price) / self.entry_price) * 100

		sl_hit = percent_move_high >= self.conf["short_sl"]
		tp_hit = percent_move_low < self.conf["short_tp"]

		current_macd = self.conf["macd"][-2+current_i:current_i]
		current_signal = self.conf["signal"][-2+current_i:current_i]
		#Close short with stop-loss
		if sl_hit and not tp_hit:
			self.short_position = False

			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = abs(self.conf["short_sl"] * self.margin) #positive

			#unittest
			assert fees >= 0, "fees are negative!"
			assert trade >= 0, "trade are negative!"

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
			assert fees >= 0, "fees are negative!"
			assert trade >= 0, "trade are negative!"

			self.profit +=  trade - fees

			#Metrics
			self.winning_trades += 1
			self.winning_short_trades += 1
			self.profit_over_trades.append(self.profit)

		elif tp_hit and sl_hit:
			self.short_position = False
			self.both_hit += 1
		
		
		#Close due to long cnd
		elif self.long_cnd(current_macd, current_signal):
			self.short_position = False
			self.long_position = True
			self.long_trades += 1
			self.total_trades += 1


			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = (((current_close - self.entry_price) / self.entry_price) * 100) * self.margin
			self.entry_price = current_close
			#unittest
			assert fees >= 0, "fees are negative!"

			#If it is a loss
			if trade > 0:
				self.profit -= trade + fees

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

		self.profit_over_time = []
		self.profit_over_trades = []
		self.usd_over_time = []

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
		if self.total_trades:
			self.fitness = np.sum(self.profit_over_trades) / self.total_trades
		else:
			self.fitness = 0
