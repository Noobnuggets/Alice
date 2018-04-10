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

def setup_macd(traders, sources):
	for trader in traders:
		fast_period = trader.conf["fast_ma_period"]
		slow_period = trader.conf["slow_ma_period"]
		signal_period = trader.conf["signal_period"]

		source = trader.conf["source"]

		trader.conf["macd"], trader.conf["signal"] = MACD(sources[source], fast_period, slow_period, signal_period)


def init_population(population_amt, max_lookback):
	traders = [Trader(max_lookback=max_lookback) for _ in range(population_amt)]
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

def crossover(traders, max_lookback, mutation_factor=0.1):
	new_traders = []
	for i in range(0, len(traders)-1):
		parent_1_idx = randint(0, len(traders)-1)
		parent_2_idx = randint(0, len(traders)-1)
		while parent_1_idx == parent_2_idx:
			parent_1_idx = randint(0, len(traders)-1)
			parent_2_idx = randint(0, len(traders)-1)

		parent_1 = traders[parent_1_idx]
		parent_2 = traders[parent_2_idx]
		parent_1_dna = parent_1.conf
		parent_2_dna = parent_2.conf

		convolving_attr = ["fast_ma_period", "slow_ma_period", "signal_period", "long_tp", "short_tp", "long_sl", "short_sl"]

		conf = {} #New DNA
		for attr in convolving_attr:
			if uniform(0, 1) <= mutation_factor:
				conf[attr] = traders[randint(0, len(traders)-1)].conf[attr]#choice([parent_1_dna[attr], parent_2_dna[attr]])
			else:
				conf[attr] = (parent_1_dna[attr] + parent_2_dna[attr])/2
		conf["fast_ma_period"] = int(round(conf["fast_ma_period"]))
		conf["slow_ma_period"] = int(round(conf["slow_ma_period"]))
		conf["signal_period"] = int(round(conf["signal_period"]))
		conf["long_tp"] = int(round(conf["long_tp"]))
		conf["short_tp"] = int(round(conf["short_tp"]))
		conf["long_sl"] = int(round(conf["long_sl"]))
		conf["short_sl"] = int(round(conf["short_sl"]))
		choice_attr = ["source"]

		for attr in choice_attr:
			if uniform(0, 1) <= mutation_factor:
				conf[attr] = choice(traders).conf[attr]
			else:
				conf[attr] = choice([parent_1_dna[attr], parent_2_dna[attr]])


		#Unittest
		new_trader = Trader(conf=conf, max_lookback=max_lookback)

		assert new_trader.conf["long_tp"] > 0, "long_tp is invalid: " + str(new_trader.conf["long_tp"])
		assert new_trader.conf["long_sl"] < 0, "long_sl is invalid: " + str(new_trader.conf["long_sl"])
		assert new_trader.conf["short_tp"] < 0, "short_tp is invalid: " + str(new_trader.conf["short_tp"])
		assert new_trader.conf["short_sl"] > 0, "short_sl is invalid: " + str(new_trader.conf["short_sl"])
		
		new_traders.append(new_trader)
	print("Kids added:", len(new_traders))
	return new_traders

def fresh_dna(current_traders, population_amt, max_lookback, best_trader):
	dna_added = 0
	repeat_added = 0
	while len(current_traders) < population_amt:
		if uniform(0, 1) < 0.05:
			current_traders.append(best_trader)
			repeat_added += 1
		else:
			current_traders.append(Trader(max_lookback=max_lookback))
			dna_added += 1

	assert len(current_traders) == population_amt, "Missmatching len(current_traders) and population_amt\nlen(current_traders): " + str(len(current_traders))+"\npopulation_amt: " + str(population_amt)
	print("New Traders added:", dna_added)
	print("Best trader re-added:", repeat_added)
	print()
	print()
	return current_traders


def train(candle_period, max_lookback, population_amt, generations, mutation_factor, max_survival_factor):
	ohlcv = load_ohlcv(candle_period=candle_period, path="Data/train.csv")

	opens = ohlcv.open.values
	highs = ohlcv.high.values
	lows = ohlcv.low.values
	closes = ohlcv.close.values
	vol = ohlcv.volume.values
	print("Candles:", len(opens))

	sources = {
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

	traders = init_population(population_amt=population_amt, max_lookback=max_lookback)
	best_trader = traders[0]
	setup_macd(traders, sources=sources)

	for gen in range(generations):

		#Test every trader on every trade oppurtinity/candle
		for i in range(max_lookback+12+2, len(closes)): #+9 cus maximum signal line smoothing
			for trader in traders:
				trader.event(i, closes[i], lows[i], highs[i])
				if trader.fitness > best_trader.fitness:
					best_trader = trader

		
		#Generation done
		#Collect metrics on a per-generation basis
		traders = calculate_fitness(traders)
		average_fitness.append(average_fitness_per_generation(traders))

		best_fitness.append(traders[0].fitness)
		#Sort traders based on performance
		traders = sort_traders(traders)
		conf = traders[0].conf
		print(gen, "best profit:", traders[0].profit)
		print(gen, "best:", traders[0].fitness)
		print(gen, "avg:", average_fitness[gen])


		if not gen+1 == generations:
			survival_rate = gen/generations
			if survival_rate > max_survival_factor:
				survival_rate = max_survival_factor
			print("survival_rate:", survival_rate)
			#Remove the worst traders
			#Create children from the best traders, aka crossover
			traders = kill_worst(traders, survival_rate=survival_rate)
			traders = crossover(traders, max_lookback, mutation_factor=mutation_factor ) #Crossover creates some individuals without fitness

			traders = fresh_dna(traders, population_amt, max_lookback, best_trader)
			setup_macd(traders, sources=sources)

			#Reset metrics for traders for next generation
			
			reset_metrics(traders)

	return traders, average_fitness, best_fitness, best_trader

def validate(traders, candle_period, max_lookback):
	valid_ohlcv = load_ohlcv(candle_period=candle_period, path="Data/validation.csv")

	valid_opens = valid_ohlcv.open.values
	valid_highs = valid_ohlcv.high.values
	valid_lows = valid_ohlcv.low.values
	valid_closes = valid_ohlcv.close.values
	valid_vol = valid_ohlcv.volume.values
	print("valid Candles:", len(valid_opens))

	valid_sources = {
		"open":valid_opens,
		"high":valid_highs,
		"low":valid_lows,
		"close":valid_closes,
		"hl2":(valid_highs+valid_lows)/2,
		"hlc3":(valid_highs+valid_lows+valid_closes)/3,
		"ohlc4":(valid_opens+valid_highs+valid_lows+valid_closes)/4
		}

	setup_macd(traders, sources=valid_sources)

	#Metrics
	average_fitness = []
	best_fitness = []
	#Test every trader on every trade oppurtinity/candle
	reset_metrics(traders)
	for i in range(max_lookback+3, len(valid_closes)):
		for trader in traders:
			trader.event(i, valid_closes[i], valid_lows[i], valid_highs[i])