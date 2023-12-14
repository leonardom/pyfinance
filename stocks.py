from bs4 import BeautifulSoup
from utils import normalize, export_to_csv
import datetime
import sys
import requests
import time

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Sec-Fetch-Mode': 'navigate',
    'Host': 'www.fundamentus.com.br',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
    'Referer': 'https://www.fundamentus.com.br/detalhes.php?papel=BRAP4',
    'Connection': 'keep-alive',
}

def get_dividends(ticker):
  params = {
    'papel': ticker,
    'tipo': '2',
  }
  response = requests.get('https://www.fundamentus.com.br/proventos.php', params=params, headers=headers)
  #print(response.text)
  soup = BeautifulSoup(response.text, 'html.parser')
  table = soup.find(id='resultado-anual')
  data = {}
  for tr in table.find_all('tr'):
    tds = tr.find_all('td')
    if len(tds) == 2:
      key = tds[0].text
      value = normalize(tds[1].text)
      data.update({key: value})

  return data

def calculate_average(data, years=5):
  total = 0
  count = 0
  current_year = str(datetime.date.today().year)
  for year in data:
    if year != current_year and count < years:
      total += data[year]
      count += 1
  return total / count


def get_data(ticker):
  dividends = get_dividends(ticker)
  data = {
    'ticker': ticker,
    'dy_5y': calculate_average(dividends),
  }
  return data


def main():
  if len(sys.argv) == 1:
    print("Missing tickers arguments")
    return
  tickers = sys.argv[1:]
  data = []
  for ticker in tickers:
    print(f"Getting data for {ticker}...")
    data.append(get_data(ticker))
    time.sleep(5)

  export_to_csv(data, 'stocks.csv')
  print(f"All done! :)")

if __name__ == "__main__":
  main()