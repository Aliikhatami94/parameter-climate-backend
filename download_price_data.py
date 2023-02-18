import asyncio
import requests
import time


# Download the price data from the web dynamically and asynchronously using asyncio
async def download_price_data():
    # Download the price data from the web dynamically
    month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    year = range(1998, int(time.strftime("%Y")) + 1)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Log the start time
    start = time.time()

    # run an asynchronous loop of requests
    for y in year:
        for m in month:
            url = f'https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_{y}{m}_NSW1.csv'
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                with open(f'price_data/{y}{m}.csv', 'wb') as f:
                    f.write(r.text.encode('utf-8'))
                    print(f'Downloaded {y}{m}.csv')
            else:
                print(f'No data for {m}/{y}')
                pass

    print('Download complete!')
    print(f'Time taken on 1: {time.time() - start}')

if __name__ == '__main__':
    asyncio.run(download_price_data())
    print('Done!')