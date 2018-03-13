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
