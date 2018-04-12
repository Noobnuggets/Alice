import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from random import uniform, randint, choice
from financial_functions import *
from utils import *

class Trader():
	def __init__(self, max_lookback, starting_usd=100000, fee=0.2, conf=None, margin=3.3, margin_fee = 0.015):
		self.percent_per_trade = 5
		self.fee = fee
		self.starting_usd = starting_usd
		#Metrics
		self.metrics = {"usd":starting_usd,
						"usd_over_time":[],

						"profit":0,
						"profit_over_time":[],
						"profit_over_trades":[],

						"long_trades_entry":0, #Normal condition entry
						"short_trades_entry":0, ##Normal condition entry

						"long_trades_flip":0, #Flip from long trade to short trade
						"short_trades_flip":0, #Flip from short trade to long trade

						"long_trades_hit":0, #Long trades hit TP
						"long_trades_miss":0, #Long Trades hit SL

						"short_trades_hit":0, #Short trades hit TP
						"short_trades_miss":0, #Short trade hit SL

						"total_trades":0, #Total trades taken
						"sl_and_tp_hit":0, #Both hit

						"long_trades_flip_win":0, #Flip from long trade with a profit
						"short_trades_flip_win":0, #Flip from a short trade with a profit

						"long_trades_flip_miss":0, #Flip from a long trade with a loss
						"short_trades_flip_miss":0 #Flip from a short trade with a loss
						}

		#conf stuff
		sources = ["open", "close", "low", "high", "hl2", "hlc3", "ohlc4"]
		self.conf = conf
		
		max_range = 100
		min_range = 50

		max_sl = 100
		min_sl = 50
		

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
			"volume_factor":uniform(1, 2)
			}

		#Trading
		self.long_position = False
		self.short_position = False
		self.entry_price = None

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
		return (signal[0] > macd[0] and signal[1] < macd[1]) or (macd[0] < 0 and macd[1] > 0)
		#return macd[0] < 0 and macd[1] > 0

	def short_cnd(self, macd, signal):
		assert len(macd) == 2, "long_cnd macd invalid len: " + str(len(macd))
		assert len(signal) == 2, "long_cnd signal invalid len: " + str(len(signal))
		return (signal[0] < macd[0] and signal[1] > macd[1]) or (macd[0] > 0 and macd[1] < 0)
		#return macd[0] > 0 and macd[1] < 0
	

	def event(self, current_i, current_price, current_low, current_high): 
		assert (self.long_position and not self.short_position) or (self.short_position and not self.long_position) or (not self.short_position and not self.long_position), "More positions.."
		#Metrics
		self.metrics["profit_over_time"].append(self.metrics["profit"]) #done
		self.metrics["usd_over_time"].append(self.metrics["usd"]) #done


		current_macd = self.conf["macd"][-2+current_i:current_i]
		current_signal = self.conf["signal"][-2+current_i:current_i]
		#If not already in a position, check for potential positions
		if not self.long_position and not self.short_position:
			if self.long_cnd(current_macd, current_signal):
				self.metrics["long_trades_entry"] += 1 #done
				self.metrics["total_trades"] += 1 #done
				
				self.long_position = True
				self.entry_price = current_price

			elif self.short_cnd(current_macd, current_signal):
				self.metrics["short_trades_entry"] += 1 #done
				self.metrics["total_trades"] += 1 #done

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
			

			self.metrics["profit"] -= trade + fees

			#metrics
			self.metrics["long_trades_miss"] += 1 #done
			self.metrics["profit_over_trades"].append(self.metrics["profit"]) #done


		#Close long with take-profit
		elif tp_hit and not sl_hit:
			self.long_position = False

			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = self.conf["long_tp"] * self.margin  #positive

			#unittest
			assert fees >= 0, "fees are negative!"
			assert trade >= 0, "trade are negative!"

			self.metrics["profit"] += trade - fees

			#Metrics
			self.metrics["long_trades_hit"] += 1 #done
			self.metrics["profit_over_trades"].append(self.metrics["profit"]) #done


		elif tp_hit and sl_hit:
			self.long_position = False
			self.metrics["sl_and_tp_hit"] += 1


		#Close due to short cnd #flip
		elif self.short_cnd(current_macd, current_signal):
			self.long_position = False
			self.short_trade = True
			self.metrics["long_trades_flip"] += 1 #done
			self.metrics["total_trades"] += 1 #done

			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = (((current_close - self.entry_price) / self.entry_price) * 100) * self.margin
			self.entry_price = current_close
			#unittest
			assert fees >= 0, "fees are negative!"

			#If it is a loss
			if trade < 0:
				self.metrics["profit"] -= abs(trade) + fees

				#Metrics
				self.metrics["long_trades_flip_miss"] += 1 #done
				self.metrics["profit_over_trades"].append(self.metrics["profit"]) #done
			
			#if it is a win
			elif trade > 0:
				#Also win after fees are applied
				if trade - fees > 0:
					self.metrics["profit"] += trade - fees

					#Metrics
					self.metrics["long_trades_flip_win"] += 1 #done
					self.metrics["profit_over_trades"].append(self.metrics["profit"]) #done

				#otherwise
				else:
					self.metrics["profit"] += trade - fees #negative

					#Metrics
					self.metrics["long_trades_flip_miss"] += 1 #done
					self.metrics["profit_over_trades"].append(self.metrics["profit"]) #done

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

			self.metrics["profit"] -= trade + fees

			#metrics
			self.metrics["short_trades_miss"] += 1 #done
			self.metrics["profit_over_trades"].append(self.metrics["profit"]) #done

		#Close short with take-profit
		elif tp_hit and not sl_hit:
			self.short_position = False

			#Trades 
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = abs(self.conf["short_tp"] * self.margin) #positive

			#unittest
			assert fees >= 0, "fees are negative!"
			assert trade >= 0, "trade are negative!"

			self.metrics["profit"] +=  trade - fees

			#Metrics
			self.metrics["short_trades_hit"] += 1 #done
			self.metrics["profit_over_trades"].append(self.metrics["profit"]) #done

		elif tp_hit and sl_hit:
			self.short_position = False
			self.metrics["sl_and_tp_hit"] += 1 #done
		
		
		#Close due to long cnd
		elif self.long_cnd(current_macd, current_signal):
			self.short_position = False
			self.long_position = True

			self.metrics["short_trades_flip"] += 1 #done
			self.metrics["total_trades"] += 1 #done


			#Trades
			fees = (self.fee * 2) + (self.margin_fee * 2) #positive
			trade = (((current_close - self.entry_price) / self.entry_price) * 100) * self.margin
			
			self.entry_price = current_close
			#unittest
			assert fees >= 0, "fees are negative!"

			#If it is a loss
			if trade > 0:
				self.metrics["profit"] -= trade + fees 

				#Metrics
				self.metrics["short_trades_flip_miss"] += 1 #done
				self.metrics["profit_over_trades"].append(self.metrics["profit"]) #done
			
			#if it is a win
			elif trade < 0:
				#Also win after fees are applied
				if trade + fees < 0:
					self.metrics["profit"] += abs(trade) - fees

					#Metrics
					self.metrics["short_trades_flip_win"] += 1 #done
					self.metrics["profit_over_trades"].append(self.metrics["profit"]) #done

				#otherwise
				else:
					self.metrics["profit"] -= trade + fees #negative 

					#Metrics
					
					self.metrics["short_trades_flip_miss"] += 1 #done
					self.metrics["profit_over_trades"].append(self.metrics["profit"])


	def reset(self):

		#Metrics
		self.metrics = {"usd":self.starting_usd,
						"usd_over_time":[],

						"profit":0,
						"profit_over_time":[],
						"profit_over_trades":[],

						"long_trades_entry":0, #Normal condition entry
						"short_trades_entry":0, ##Normal condition entry

						"long_trades_flip":0, #Flip from long trade to short trade
						"short_trades_flip":0, #Flip from short trade to long trade

						"long_trades_hit":0, #Long trades hit TP
						"long_trades_miss":0, #Long Trades hit SL

						"short_trades_hit":0, #Short trades hit TP
						"short_trades_miss":0, #Short trade hit SL

						"total_trades":0, #Total trades taken
						"sl_and_tp_hit":0, #Both hit

						"long_trades_flip_win":0, #Flip from long trade with a profit
						"short_trades_flip_win":0, #Flip from a short trade with a profit

						"long_trades_flip_miss":0, #Flip from a long trade with a loss
						"short_trades_flip_miss":0, #Flip from a short trade with a loss

						"average_profit": 0,
						"average_loss": 0
						}

		#Trading
		self.long_position = False
		self.short_position = False
		self.entry_price = None
	
	def report_conf(self):
		print("Trader conf")
		print("short tp:", abs(self.conf["short_tp"]))
		print("short sl:", self.conf["short_sl"])
		print("\nlong tp:", self.conf["long_tp"])
		print("long sl:", abs(self.conf["long_sl"]))
		print("\nMACD")
		print("slow len:", self.conf["slow_ma_period"])
		print("fast len:", self.conf["fast_ma_period"])
		print("signal len:", self.conf["signal_period"])
		print("source:", self.conf["source"])

	def report_metrics(self):
		m = self.metrics
		print("Trader metrics")
		print("Total trades:", m["total_trades"])
		print("profit:", m["profit"])
		print("long trade entry cnd:", m["long_trades_entry"])
		print("short trade entry cnd:", m["short_trades_entry"])
		
		print("\nsl and tp hit:", m["sl_and_tp_hit"])
		
		print("\nlong trades TP hit:", m["long_trades_hit"])
		print("short trades TP hit:", m["short_trades_hit"])
		print("long trades SL hit:", m["long_trades_miss"])
		print("short trades SL hit:", m["short_trades_miss"])
		
		print("\nFlipped Trades")
		print("long trades flipped:", m["long_trades_flip"])
		print("short trades flipped:", m["short_trades_flip"])
		print("long trades flipped at profit:", m["long_trades_flip_win"])
		print("long trades flipped at loss:", m["long_trades_flip_miss"])
		print("short trades flipped at profit:", m["short_trades_flip_win"])
		print("short trades flipped at loss:", m["short_trades_flip_miss"])
		print("average trade:", np.sum(self.metrics["profit_over_trades"]) / self.metrics["total_trades"])




	def fitness_func(self):
		if self.metrics["total_trades"]:
			self.fitness = np.sum(self.metrics["profit_over_trades"]) / self.metrics["total_trades"]
		else:
			self.fitness = 0
		#self.fitness = self.metrics["profit"]
