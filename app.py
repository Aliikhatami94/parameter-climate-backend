# Flask environment
import json

from flask import Flask, request
from flask_cors import CORS

# Import the functions from functions.py
from functions import get_payout, get_future_price

# Create an instance of Flask
app = Flask(__name__)
CORS(app)
app.config['JSON_SORT_KEYS'] = False

# 'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
app.config['FLASK_ENV'] = 'development'
base_url = '/api/v1'


# Get future price in an hour interval
@app.route(f'{base_url}/future_price')
def future_price():
    future_price_data = get_future_price()
    response = app.response_class(response=json.dumps(future_price_data), status=200, mimetype='application/json')
    return response


# Send the payout to the front end while recieving parameters strike and trigger
@app.route(f'{base_url}/payout', methods=['GET', 'POST'])
def payout():
    current_price = request.args.get('current_price')
    trigger = request.args.get('trigger')
    strike = request.args.get('strike')
    quarter = request.args.get('quarter')
    start_year = request.args.get('start_year')
    payout_data = get_payout(current_price, trigger, strike, quarter, start_year)
    response = app.response_class(response=json.dumps(payout_data), status=200, mimetype='application/json')
    return response

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

