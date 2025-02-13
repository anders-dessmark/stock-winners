from datetime import datetime
import os
import csv

class Stock_Calculator:

	top_nbr = 3

	def __init__(self, stock_filename):
		self.filename = stock_filename
		self.last_update = 0 # timestamp

	def calculate(self):
		"""
		Returns a JSON object with the top performing stocks based on the stocks_filename file

		Assumptions:
		- The datafile provided is chronologically ordered (otherwise read the entire file and sort is before processing)
		- The datafile is resonably pruned (otherwise reading the entire file is expensive and we should use seek and binary search
		  for added data)
		"""

		old_stock_prices = dict() # last stock price from previous days (possibly several days if no trades yesterday)
		last_stock_prices = dict() # last stock price today
		current_date = None	

		if os.stat(self.filename).st_mtime == self.last_update: # no change in data file
			return self.winners

		self.last_update = os.stat(self.filename).st_mtime

		with open(self.filename, newline = '') as csvfile:
			reader = csv.DictReader(csvfile, delimiter = ';')
			for row in reader:
				row_date = datetime.strptime(row['Date'], '%Y-%m-%d %H:%M:%S').date()

				if current_date is None: # first row
					current_date = row_date

				if row_date > current_date: # found new day, add old day to old_stock_prices
					current_date = row_date
					for stock, price in last_stock_prices.items():
						old_stock_prices[stock] = price
					last_stock_prices = dict()
				last_stock_prices[row['Kod']] = float(row['Kurs'])

		# compute percentage gain and produce a sorted top list
		top_stock = list()
		for stock, price in last_stock_prices.items():
			if stock in old_stock_prices:
				percent = 100 * (price / old_stock_prices[stock] - 1)
				if len(top_stock) < self.top_nbr or percent > top_stock[-1]['percent']: # current stock might be a "winner"
					if len(top_stock) == self.top_nbr: # keep top, no need to sort the losers
						top_stock.pop()
					top_stock.append({'name': stock, 'percent': percent, 'latest': price})
				top_stock = sorted(top_stock, key = lambda x:x['percent'], reverse = True)

		# produce final result, rounding and indexing
		self.winners = list()
		for idx, stock in enumerate(top_stock):
			stock['rank'] = idx + 1
			stock['percent'] = round(stock['percent'], 2)
			self.winners.append(stock)

		return self.winners
