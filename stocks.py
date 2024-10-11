from bs4 import BeautifulSoup
from utils import normalize, export_to_csv
from gspread_utils import GoogleSpreadSheetUtil
import datetime
import sys
import requests
import time

gsu = GoogleSpreadSheetUtil('Carteira de Ações')

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Sec-Fetch-Mode': 'navigate',
    'Host': 'www.fundamentus.com.br',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
    'Connection': 'keep-alive',
}

def get_dividends(ticker):
  params = {
    'papel': ticker,
    'tipo': '2',
  }
  response = requests.get('https://www.fundamentus.com.br/proventos.php', params=params, headers=headers)
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

def get_tickers_from_gs():
  data = gsu.get_sheet_data()
  tickers = []
  for row in data[2:23]:
    if row[0]:
      tickers.append(row[0])
  return tickers

def update_gs_with_dy_5y(data):
  if input("Do you want update Google Sheets? (yes/no) ") in ["no", "n"]:
    return

  for row in data:
    cell = gsu.find_cell(row['ticker'])
    print(f"Updating {row['ticker']} into the spreadsheet row {cell.row} col 5 with {row['dy_5y']}...")
    gsu.update_cell(cell.row, 5, row['dy_5y'])

def print_divisor():
  print(f"+{'-' * 8}+{'-' * 8}+")

def print_data(data):
  print_divisor()
  print("| TICKER | D/Y 5y |")
  print_divisor()
  for row in data:
    print(f"|{row['ticker']:^8}|{row['dy_5y']:^8,.2f}|" )
  print_divisor()

def main():
  tickers = sys.argv[1:]
  if len(tickers) == 0:
    print("No tickers provided!")
    if input("Do you want to get tickers from your Google Sheets? (yes/no) ") in ["no", "n"]:
      return
    tickers = get_tickers_from_gs()
  
  data = []
  for ticker in tickers:
    print(f"Getting data for {ticker}...")
    data.append(get_data(ticker))
    time.sleep(5)

  update_gs_with_dy_5y(data)
  #export_to_csv(data, 'stocks.csv')
  print_data(data)

  print(f"All done! :)")

if __name__ == "__main__":
  main()