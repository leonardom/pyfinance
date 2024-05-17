from bs4 import BeautifulSoup
from utils import normalize, export_to_csv, export_to_excel
from gspread_utils import GoogleSpreadSheetUtil
import requests
import time
import sys

gsu = GoogleSpreadSheetUtil('Carteira de FIIs')

def get_basic_information(soup, name):
  for information in soup.find_all('div', class_='basicInformation__grid__box'):  
    pp = information.find_all('p')
    if pp[0].text.replace('\n','').strip() == name:
      return pp[1].text.replace('\n','').strip()
  return ""


def get_fii_data(ticker):
  response = requests.get(f'https://www.fundsexplorer.com.br/funds/${ticker}')
  soup = BeautifulSoup(response.text, 'html.parser')
  fii_name = soup.find('p', class_='headerTicker__content__name').text
  data = {
    'ticker': ticker.upper(),
    'nome': fii_name.upper(),
    'tipo': get_basic_information(soup, 'Tipo ANBIMA').upper(),
    'segmento': get_basic_information(soup, 'Segmento').upper(),
  }
  for indicator in soup.find_all('div', class_='indicators__box'):
    pp = indicator.find_all('p')
    key = pp[0].text.replace('\n','').strip()
    value = normalize(pp[1].text.replace('\n','').strip())
    if len(pp) > 2:
      info = pp[2].text.replace('\n','').strip()
      key = f"{key} {info}"
    data.update({ key: value })
  data = apply_multipler(data, 'Dividend Yield últ. 12 meses', 100)
  return data


def apply_multipler(data, indicator, multipler):
  for key, value in data.items():
    if key == indicator:
      data[key] = value * multipler
  return data


def get_tickers_from_gs():
  data = gsu.get_sheet_data()
  tickers = []
  for row in data[2:38]:
    tickers.append(row[0])
  return tickers
    

def update_gs_with_dy_pvp(data):
  if input("Do you want update Google Sheets? (yes/no) ") in ["no", "n"]:
    return

  for row in data:
    cell = gsu.find_cell(row['ticker'])
    print(f"Updating {row['ticker']} into the spreadsheet row {cell.row} col 5 with {row['Dividend Yield últ. 12 meses']}...")
    gsu.update_cell(cell.row, 5, row['Dividend Yield últ. 12 meses']/100.0)
    print(f"Updating {row['ticker']} into the spreadsheet row {cell.row} col 6 with {row['P/VP']}...")
    gsu.update_cell(cell.row, 6, row['P/VP'])
    time.sleep(2)

def print_divisor():
  print(f"+{'-' * 8}+{'-' * 9}+{'-' * 6}+")

def print_data(data):
  print_divisor()
  print("| TICKER | D/Y 12M | P/VP |")
  print_divisor()
  for row in data:
    print(f"|{row['ticker']:^8}|{row['Dividend Yield últ. 12 meses']:^9,.2f}|{row['P/VP']:^6,.2f}|" )
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
    data.append(get_fii_data(ticker))
    time.sleep(5)

  update_gs_with_dy_pvp(data)
  export_to_excel(data, 'fiis.xlsx')
  print_data(data)
  print(f"All done! :)")

if __name__ == "__main__":
  main()