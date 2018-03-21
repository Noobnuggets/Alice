from financial_functions import *
from agent import Trader
from operator import attrgetter
from random import uniform, choice
def average_profit_per_generation(traders):
	avg_profit = 0
	for trader in traders:
		avg_profit += trader.profit
	return avg_profit/len(traders)

def setup_mas(traders, ma_sources):
	for trader in traders:
		period = trader.conf["ma_period"]
		ma_func = trader.conf["ma_func"]
		ma_source = trader.conf["ma_source"]
		trader.conf["ma"] = ma_func(ma_sources[ma_source], period)


def init_population(population_amt):
	traders = [Trader() for _ in range(population_amt)]
	return traders

def sort_traders(traders):
	traders.sort(key = attrgetter('profit'))
	return traders

def reset_metrics(traders):
	for trader in traders:
		trader.reset()

def kill_worst(traders, survival_factor=0.7):
	new_traders = [traders[i] for i in range(int(len(traders)*survival_factor))]
	return new_traders

def crossover(traders, mutation_factor=0.01, starting_usd=100000, fee=0.1):
	new_traders = []
	for i in range(0, len(traders)-1, 2):
		parent_1_dna = traders[i].conf
		parent_2_dna = traders[i+1].conf

		convolving_attr = ["ma_period", "long_tp", "short_tp", "long_sl", "short_sl"]

		conf = {} #New DNA
		for attr in convolving_attr:
			conf[attr] = (parent_1_dna[attr] + parent_2_dna[attr])/2
		conf["ma_period"] = int(round(conf["ma_period"]))

		choice_attr = ["ma_source", "ma_func"]

		for attr in choice_attr:
			conf[attr] = choice([parent_1_dna[attr], parent_2_dna[attr]])


		#Unittest

		new_traders.append(Trader(starting_USD=starting_usd, fee=fee, conf=conf))
	return new_traders



		