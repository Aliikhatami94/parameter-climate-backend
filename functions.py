import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import logging.config

# Log everything, and send it to stderr.
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-8s %(message)s',
)

# Define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# Set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# Tell the handler to use this format
console.setFormatter(formatter)

# Add the handler to the root logger
logging.getLogger('').addHandler(console)

# Create a custom logger
logger = logging.getLogger(__name__)

# Set pandas options
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 100)


# Weather data
def get_tmax_data(quarter):
    pd.set_option('display.max_columns', 20)

    df = pd.read_csv('weather_data/IDCJAC0010_066037_1800_Data.csv')
    df = df[['Year', 'Month', 'Day', 'Maximum temperature (Degree C)']]

    # Convert Year Month Day to a single date column
    df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])

    df['quarter'] = pd.PeriodIndex(df['Date'], freq='Q')

    # Filter data frame to specified quarter number
    filtered_df = df[df['quarter'].astype(str).str.endswith(f"Q{quarter}")]

    # drop the quarter, year, month and day columns
    filtered_df = filtered_df.drop(['Month', 'Day', 'quarter'], axis=1)

    return filtered_df


# Future price
def get_future_price():
    url = "https://www.asxenergy.com.au/futures_au"

    # Create a new instance of the Firefox driver
    options = webdriver.ChromeOptions()

    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    # Navigate to the URL
    driver.get(url)

    # Wait for the table to load
    table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table")))

    # Get all the rows that the td class=market-dataset-state and td class=settle
    tds = table.find_elements(By.XPATH, "//td")

    # Get the text from the td elements
    td = [i.text for i in tds]

    # Get the index of the first future price value
    i_at_q4 = 53
    prices = []

    # Close the browser
    driver.quit()

    # Get the future price for the next 4 quarters
    for i in range(0, 4):
        prices.append(td[i_at_q4])
        i_at_q4 += 7

    # Convert the list to dictionary
    prices = dict(zip(['Q1', 'Q2', 'Q3', 'Q4'], prices))

    return prices


# Average Price data
def quarter_avg_price(quarter):
    month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    year = range(1999, int(time.strftime("%Y")))

    # concatenate all the csv files into one dataframe
    df = pd.concat([pd.read_csv(f'price_data/{y}{m}.csv') for y in year for m in month], ignore_index=True)

    df['quarter'] = pd.PeriodIndex(df['SETTLEMENTDATE'], freq='Q').astype(str)

    # Group the dataframe by quarter and calculate the mean of RRP column for each group
    quarterly_avg_price = df.groupby('quarter')['RRP'].mean()

    # Filter the series to the quarter we want
    q4_avg_price = quarterly_avg_price[quarterly_avg_price.index.str.contains(f"Q{quarter}")]

    # Extract the year from the quarter index and create a new column from it
    q4_avg_price = q4_avg_price.reset_index()
    q4_avg_price['year'] = q4_avg_price['quarter'].str.extract('(\d{4})')
    q4_avg_price['avg_price'] = q4_avg_price['RRP']

    # Drop the quarter and RRP columns
    q4_avg_price = q4_avg_price.drop(['quarter', 'RRP'], axis=1)

    return q4_avg_price


# Price data per quarter
def get_quarter_prices(quarter):
    month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    year = range(1999, int(time.strftime("%Y")))

    # concatenate all the csv files into one dataframe
    df = pd.concat([pd.read_csv(f'price_data/{y}{m}.csv') for y in year for m in month], ignore_index=True)

    # Convert SETTLEMENTDATE column to PeriodIndex with quarterly frequency
    df['SETTLEMENTDATE'] = pd.to_datetime(df['SETTLEMENTDATE'], format='%Y/%m/%d %H:%M')
    df['quarter'] = pd.PeriodIndex(df['SETTLEMENTDATE'], freq='Q')

    # Filter data frame to specified quarter number
    filtered_df = df[df['quarter'].astype(str).str.endswith(f"Q{quarter}")]

    # Drop quarter column
    filtered_df = filtered_df.drop(['quarter'], axis=1)

    return filtered_df[['SETTLEMENTDATE', 'RRP']]


def get_scaled_price(current_price, quarter):

    # Load the 5min price data for the quarter
    df1 = get_quarter_prices(quarter)

    # Load the average price data for the quarter
    df2 = quarter_avg_price(quarter)

    # Convert the date column in df1 to a datetime format
    df1['SETTLEMENTDATE'] = pd.to_datetime(df1['SETTLEMENTDATE'], format='%Y/%m/%d %H:%M')

    # Extract the year from the date column in df1 as an integer
    df1['year'] = df1['SETTLEMENTDATE'].dt.year.astype(int)

    # Convert the year column in df2 to an integer
    df2['year'] = df2['year'].astype(int)

    # Merge the two dataframes on the year column
    merged_df = pd.merge(df1, df2, on='year')

    # Calculate the new column by dividing the price column by the average_price column
    merged_df['scaled_price'] = (current_price * merged_df['RRP']) / merged_df['avg_price']

    return merged_df.reset_index(drop=True)


def get_payout(current_price, trigger, strike, quarter="4", start_year="1999"):
    # Convert the input parameters to the correct data types
    current_price, trigger, strike, quarter, start_year = float(current_price), int(trigger), int(strike), int(quarter), int(start_year)

    # Create log statements for the payout function
    logger.info(f'Payout function called with trigger={trigger}, strike={strike}, quarter={quarter}')

    # Load scaled price data
    df = get_scaled_price(current_price, quarter)

    # Load weather data
    weather_data = get_tmax_data(quarter)

    # Find matching dates in weather data and scaled price data and create a tmax column
    df['tmax'] = df['SETTLEMENTDATE'].dt.date.map(weather_data.set_index('Date')['Maximum temperature (Degree C)'])

    # Calculate the payout for each row
    df['payout'] = df.apply(lambda x: max(int(x['scaled_price']) - strike, 0) if int(x['tmax']) >= trigger else 0, axis=1)

    # Create log statements for the payout function

    logger.info(f'Payout function returned {df["payout"].sum()}')


    # Sum up all the payouts for each year and return a series
    annual_payout_df = df.groupby(df['SETTLEMENTDATE'].dt.year)['payout'].sum()

    # Filter the series to the start year
    annual_payout_df = annual_payout_df[annual_payout_df.index >= start_year]

    # return in format of json string
    # output format: {"year": [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019], "payout": [20, 30, 40, 50, 60, 70, 80, 90, 100, 110]}
    return {'year': annual_payout_df.index.tolist(), 'payout': annual_payout_df.values.tolist()}


