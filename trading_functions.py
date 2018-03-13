import numpy as np
import pandas as pd
def walk_forward(price, sign, slippage=0, stop=10):
	slippage = slippage
	stop_amount = stop

	#Go long
	if sign == 1:
		initial_stop_loss = price[0] - stop_amount

		stop_loss = initial_stop_loss
		for i in range(1, len(price)): #Start at 1 and walk forward
			move = price[i] - price[i-1]

			#Continue to move stop-loss
			if move > 0 and (price[i] - stop_amount) > initial_stop_loss:
				stop_loss = price[i] - stop_amount

			#Close the trade
			elif price[i] < stop_loss:
				if i == 1:
					return 0, 1 #Dont reward odd behaviour
				return (stop_loss - price[0]) - slippage, 0
	
	#Go short
	elif sign == -1:
		initial_stop_loss = price[0] + stop_amount

		stop_loss = initial_stop_loss
		for i in range(1, len(price)): #Start at 1 and walk forward
			move = price[i] - price[i-1]

			#Continue to move stop-loss
			if move < 0 and (price[i] + stop_amount) < initial_stop_loss:
				stop_loss = price[i] + stop_amount

			#Close the trade
			elif price[i] > stop_loss:
				if i == 1:
					return 0, 1 #Dont reward closing on first candle
				return (price[0] - stop_loss) - slippage, 0
	else:
		print("Something went wrong!")
		print(price, sign, slippage, stop)

def walk_forward2(prices, highs, lows, sign, stop_loss_percentage=-5, target_percent=5, slippage=-0.001, fee_per_trade_percent=0.2, lots=1, margin=1):
	#stop_loss_percentage should be a negative number
	#target_percent should be a positive number
	target_hit = False
	if sign == 1:
		#Long
		fee = prices[0] * (fee_per_trade_percent/100)
		entry_price = prices[0] + slippage + fee

		target_price = entry_price * ((target_percent / 100) + 1) #Percent number to factor
		stop_loss_price = entry_price * (1 - (target_percent / 100)) #100 percent minus factor 
		for i in range(1, len(prices)):
			#Check for stoploss hit
			#Stop loss check first, always assume worst case scenario
			if lows[i] <= stop_loss_price: #Less than or equal, worst case scenario
				profit_percent = ((stop_loss_price-entry_price)/entry_price) * 100 * margin * lots #How much percent profit was made from the entry price buying 1 lot of the currency
				return profit_percent
			#Check for hitting target
			elif highs[i] > target_price:
				profit_percent = ((target_price-entry_price)/entry_price) * 100 * margin * lots #How much percent profit was made from the entry price buying 1 lot of the currency
				return profit_percent
	elif sign == -1
		#Short
	else:
		print("Something went wrong!")