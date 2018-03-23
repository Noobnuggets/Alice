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


def init_population(population_amt, ma_maximum_period):
	traders = [Trader(ma_maximum_period=ma_maximum_period) for _ in range(population_amt)]
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

def crossover(traders, ma_maximum_period, mutation_factor=0.1):
	new_traders = []
	parent_idxs = []
	for i in range(0, len(traders)-1, 2):
		parent_1_idx = randint(0, len(traders)-1)
		parent_2_idx = randint(0, len(traders)-1)
		while parent_1_idx == parent_2_idx or parent_1_idx in parent_idxs or parent_2_idx in parent_idxs:
			parent_1_idx = randint(0, len(traders)-1)
			parent_2_idx = randint(0, len(traders)-1)

		parent_idxs.append(parent_1_idx)
		parent_idxs.append(parent_2_idx)
		parent_1 = traders[parent_1_idx]
		parent_2 = traders[parent_2_idx]
		parent_1_dna = parent_1.conf
		parent_2_dna = parent_2.conf

		convolving_attr = ["ma_period", "long_tp", "short_tp", "long_sl", "short_sl"]

		conf = {} #New DNA
		for attr in convolving_attr:
			if uniform(0, 1) <= mutation_factor:
				conf[attr] = traders[randint(0, len(traders)-1)].conf[attr]#choice([parent_1_dna[attr], parent_2_dna[attr]])
			elif uniform(0, 1) <= mutation_factor:
				conf[attr] = choice([parent_1_dna[attr], parent_2_dna[attr]])
			else:
				conf[attr] = (parent_1_dna[attr] + parent_2_dna[attr])/uniform(1.9, 2.1)
		conf["ma_period"] = int(round(conf["ma_period"]))

		choice_attr = ["ma_source", "ma_func"]

		for attr in choice_attr:
			if uniform(0, 1) <= mutation_factor:
				conf[attr] = choice(traders).conf[attr]
			else:
				conf[attr] = choice([parent_1_dna[attr], parent_2_dna[attr]])


		#Unittest
		new_trader = Trader(conf=conf, ma_maximum_period=ma_maximum_period)

		assert type(new_trader.USD) is int or type(new_trader.USD) is float, "starting_USD is invalid: " + str(type(new_trader.USD))
		assert new_trader.conf["long_tp"] > 0, "long_tp is invalid: " + str(new_trader.conf["long_tp"])
		assert new_trader.conf["long_sl"] < 0, "long_sl is invalid: " + str(new_trader.conf["long_sl"])
		assert new_trader.conf["short_tp"] < 0, "short_tp is invalid: " + str(new_trader.conf["short_tp"])
		assert new_trader.conf["short_sl"] > 0, "short_sl is invalid: " + str(new_trader.conf["short_sl"])
		assert type(new_trader.conf["ma_period"]) is int, "ma_period is invalid type: " + str(type(new_trader.conf["ma_period"]))
		assert new_trader.conf["ma_period"] >= 3 and new_trader.conf["ma_period"] <= ma_maximum_period, "ma_period is invalid: " + str(new_trader.conf["ma_period"])
		
		new_traders.append(new_trader)
	return new_traders

def fresh_dna(current_traders, population_amt, ma_maximum_period):
	while len(current_traders) < population_amt:
		current_traders.append(Trader(ma_maximum_period=ma_maximum_period))

	assert len(current_traders) == population_amt, "Missmatching len(current_traders) and population_amt\nlen(current_traders): " + str(len(current_traders))+"\npopulation_amt: " + str(population_amt)

	return current_traders


def train(candle_period, ma_maximum_period, population_amt, generations, survival_rate, mutation_factor):
	ohlcv = load_ohlcv(candle_period=candle_period)

	opens = ohlcv.open.values
	highs = ohlcv.high.values
	lows = ohlcv.low.values
	closes = ohlcv.close.values
	vol = ohlcv.volume.values
	print("Candles:", len(opens))

	ma_sources = {
		"open":opens,
		"high":highs,
		"low":lows,
		"close":closes,
		"hl2":(highs+lows)/2,
		"hlc3":(highs+lows+closes)/3,
		"ohlc4":(opens+highs+lows+closes)/4
		}

	#Metrics
	average_fitness = []
	best_fitness = []

	traders = init_population(population_amt=population_amt, ma_maximum_period=ma_maximum_period)
	setup_mas(traders, ma_sources=ma_sources)

	for gen in range(generations):

		#Test every trader on every trade oppurtinity/candle
		for i in range(ma_maximum_period+3, len(closes)):
			for trader in traders:
				trader.event(i, closes[i], lows[i], highs[i])

		
		#Generation done
		#Collect metrics on a per-generation basis
		traders = calculate_fitness(traders)
		average_fitness.append(average_fitness_per_generation(traders))


		#Sort traders based on performance
		traders = sort_traders(traders)

		best_fitness.append(traders[0].fitness)
		print(gen, "best:", traders[0].fitness)
		print(gen, "avg:", average_fitness[gen])
		print()

		if not gen+1 == generations:
			#Remove the worst traders
			#Create children from the best traders, aka crossover
			traders = kill_worst(traders, survival_rate=survival_rate)
			traders = crossover(traders, ma_maximum_period, mutation_factor=mutation_factor ) #Crossover creates some individuals without fitness

			traders = fresh_dna(traders, population_amt, ma_maximum_period)
			setup_mas(traders, ma_sources=ma_sources)

			#Reset metrics for traders for next generation
			
			reset_metrics(traders)

	return traders, average_fitness, best_fitness

def validate(traders, candle_period, ma_maximum_period):
	valid_ohlcv = load_ohlcv_valid(candle_period=candle_period)

	valid_opens = valid_ohlcv.open.values
	valid_highs = valid_ohlcv.high.values
	valid_lows = valid_ohlcv.low.values
	valid_closes = valid_ohlcv.close.values
	valid_vol = valid_ohlcv.volume.values
	print("valid Candles:", len(valid_opens))

	valid_ma_sources = {
		"open":valid_opens,
		"high":valid_highs,
		"low":valid_lows,
		"close":valid_closes,
		"hl2":(valid_highs+valid_lows)/2,
		"hlc3":(valid_highs+valid_lows+valid_closes)/3,
		"ohlc4":(valid_opens+valid_highs+valid_lows+valid_closes)/4
		}

	setup_mas(traders, ma_sources=valid_ma_sources)

	#Metrics
	average_fitness = []
	best_fitness = []
	#Test every trader on every trade oppurtinity/candle
	reset_metrics(traders)
	for i in range(ma_maximum_period+3, len(valid_closes)):
		for trader in traders:
			trader.event(i, valid_closes[i], valid_lows[i], valid_highs[i])