from flask import Flask, jsonify
import sys
from stock_calculator import Stock_Calculator

app = Flask(__name__)

calculator = None

@app.route('/winners', methods=['GET'])
def get_winners():
	return jsonify({'winners': calculator.calculate()})

def main():
	global calculator

	if len(sys.argv) != 2:
		print('Usage: python stock_api.py <csv file with stock prices>')
		return

	calculator = Stock_Calculator(sys.argv[1])
	app.run()


if __name__ == '__main__':
	main()

