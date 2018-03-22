from financial_functions import *
from agent import Trader
from operator import attrgetter
from random import uniform, choice, randint
def calculate_fitness(traders):
	new_traders = traders
	for trader in traders:
		trader.fitness_func()
	return new_traders
def average_fitness_per_generation(traders):
	avg_fitness = 0
	for trader in traders:
		avg_fitness += trader.fitness
	return avg_fitness/len(traders)

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
	traders.sort(key = attrgetter('fitness'), reverse=True)
	return traders

def reset_metrics(traders):
	for trader in traders:
		trader.reset()

def kill_worst(traders, survival_rate):
	assert traders[0].fitness >= traders[1].fitness, "Traders are sorted wrong!"
	return [traders[i] for i in range(int(round(len(traders)*survival_rate)))]
	
	
	#return [traders[i] for i in range(int(len(traders)*survival_factor))]

def crossover(traders, mutation_factor=0.1, starting_usd=100000, fee=0):
	new_traders = []
	for i in range(0, len(traders)-1, 2):
		parent_1 = traders[i]
		parent_2 = traders[i+1]
		parent_1_dna = parent_1.conf
		parent_2_dna = parent_2.conf

		convolving_attr = ["ma_period", "long_tp", "short_tp", "long_sl", "short_sl"]

		conf = {} #New DNA
		for attr in convolving_attr:
			if uniform(0, 1) <= mutation_factor:
				conf[attr] = choice([parent_1_dna[attr], parent_2_dna[attr]])
			else:
				conf[attr] = (parent_1_dna[attr] + parent_2_dna[attr])/2
		conf["ma_period"] = int(round(conf["ma_period"]))

		choice_attr = ["ma_source", "ma_func"]

		for attr in choice_attr:
			if parent_1.fitness > parent_2.fitness:
				conf[attr] = parent_1_dna[attr]

			elif parent_2.fitness > parent_1.fitness:
				conf[attr] = parent_2_dna[attr]
			else:
				conf[attr] = choice([parent_1_dna[attr], parent_2_dna[attr]])


		#Unittest
		new_trader = Trader(starting_USD=starting_usd, fee=fee, conf=conf)

		assert type(new_trader.USD) is int or type(new_trader.USD) is float, "starting_USD is invalid: " + str(type(new_trader.USD))
		assert new_trader.conf["long_tp"] > 0, "long_tp is invalid: " + str(new_trader.conf["long_tp"])
		assert new_trader.conf["long_sl"] < 0, "long_sl is invalid: " + str(new_trader.conf["long_sl"])
		assert new_trader.conf["short_tp"] < 0, "short_tp is invalid: " + str(new_trader.conf["short_tp"])
		assert new_trader.conf["short_sl"] > 0, "short_sl is invalid: " + str(new_trader.conf["short_sl"])
		assert type(new_trader.conf["ma_period"]) is int, "ma_period is invalid type: " + str(type(new_trader.conf["ma_period"]))
		assert new_trader.conf["ma_period"] >= 3 and new_trader.conf["ma_period"] <= 50, "ma_period is invalid: " + str(new_trader.conf["ma_period"])
		
		new_traders.append(new_trader)
	return new_traders

def fresh_dna(current_traders, population_amt):
	while len(current_traders) < population_amt:
		current_traders.append(Trader())

	assert len(current_traders) == population_amt, "Missmatching len(current_traders) and population_amt\nlen(current_traders): " + str(len(current_traders))+"\npopulation_amt: " + str(population_amt)

	return current_traders


def train(candle_period, ma_maximum_period, population_amt, generations, survival_rate, mutation_factor)