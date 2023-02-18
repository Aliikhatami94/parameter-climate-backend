# Parameter Climate Backend

This repository contains the Flask application for the Parameter Climate project. The application provides API endpoints to retrieve future price data and calculate the payout based on the provided parameters. Here are the instructions on how to run the application:

## Prerequisites

Before running the application, you need to have the following installed on your system:

- Python 3
- Flask

## Running the Application

To run the application, follow these steps:

1. Clone the repository to your local machine using `git clone https://github.com/Aliikhatami94/parameter-climate-backend.git`.

2. Open your terminal or command prompt and navigate to the root directory of the cloned repository.

3. Use the following command to install the required dependencies:

    ```pip install -r requirements.txt```

4. Use the following command to start the Flask development server: The page will reload when you make changes. You may also see any lint errors in the console.

    ```flask run```

    This will start the Flask development server on `http://localhost:5000`.

5. Open your web browser and go to `http://localhost:5000/api/v1/future_price` to retrieve the future price data.

6. To calculate the payout, make a GET or POST request to `http://localhost:5000/api/v1/payout` with the following parameters:

- `current_price`: The current price.
- `trigger`: The maximum temperature trigger.
- `strike`: The strike price.
- `quarter`: The specific quarter.
- `start_year`: The starting year.

For example, you can use `http://localhost:5000/api/v1/payout?current_price=100&trigger=80&strike=90&quarter=Q1&start_year=2010` to calculate the payout.

You should receive a JSON response containing the payout data.
