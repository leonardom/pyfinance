from utils import normalize, export_to_csv, export_to_excel
from gspread_utils import GoogleSpreadSheetUtil
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time
import sys

gsu = GoogleSpreadSheetUtil('Carteira de FIIs')
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
browser = webdriver.Chrome(options=options)


def get_fii_data(ticker):
  data = {
    'ticker': ticker.upper(),
  }
  browser.get(f"https://www.fundsexplorer.com.br/funds/{ticker.upper()}")
  data['valor_cota'] = normalize(browser.find_element(By.XPATH, '//*[@id="carbon_fields_fiis_header-2"]/div/div/div[1]/div[1]/p').text)
  data['liquidez_media_diaria'] = normalize(browser.find_element(By.XPATH, '//*[@id="indicators"]/div[1]/p[2]/b').text)
  data['ultimo_rendimento'] = normalize(browser.find_element(By.XPATH, '//*[@id="indicators"]/div[2]/p[2]/b').text)
  data['dividend_yield_12m'] = normalize(browser.find_element(By.XPATH, '//*[@id="indicators"]/div[3]/p[2]/b').text) * 100
  data['p_vp'] = normalize(browser.find_element(By.XPATH, '//*[@id="indicators"]/div[7]/p[2]/b').text)
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
    print(f"Updating {row['ticker']} into the spreadsheet row {cell.row} col 5 with {row['dividend_yield_12m']}...")
    gsu.update_cell(cell.row, 5, row['dividend_yield_12m']/100.0)
    print(f"Updating {row['ticker']} into the spreadsheet row {cell.row} col 6 with {row['p_vp']}...")
    gsu.update_cell(cell.row, 6, row['p_vp'])
    time.sleep(2)

def print_divisor():
  print(f"+{'-' * 8}+{'-' * 9}+{'-' * 6}+")

def print_data(data):
  print_divisor()
  print("| TICKER | D/Y 12M | P/VP |")
  print_divisor()
  for row in data:
    print(f"|{row['ticker']:^8}|{row['dividend_yield_12m']:^9,.2f}|{row['p_vp']:^6,.2f}|" )
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
  # export_to_excel(data, 'fiis.xlsx')
  print_data(data)
  browser.quit()
  print(f"All done! :)")

if __name__ == "__main__":
  main()