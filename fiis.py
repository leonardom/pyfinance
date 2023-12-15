from bs4 import BeautifulSoup
from utils import normalize, export_to_csv, export_to_excel
import requests
import time

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
    

def main():

  # tickers = ['LGCP11','VGHF11', 'BTCI11', 'GALG11','MCHF11','XPCA11','VGIR11','VINO11']
  tickers = [
    'RZTR11','BRCO11','XPLG11','GTWR11','BTAL11','KNRI11','VGHF11',
    'HGLG11','CPTS11','BCFF11','DEVA11','HCTR11','SNAG11','BTCI11',
    'RZAG11','FVPQ11','TGAR11','VISC11','JSRE11','KNCR11','BRCR11',
    'RVBI11','HGBS11','VILG11','PVBI11','FIGS11','MXRF11','LVBI11',
    'JSAF11','SNFF11','HTMX11','MCHF11','RBRR11','TVRI11','VINO11',
    'IRDM11'
  ]
  # tickers = ['RZTR11']

  data = []
  for ticker in tickers:
    print(f"Getting data for {ticker}...")
    data.append(get_fii_data(ticker))
    time.sleep(5)

  export_to_excel(data, 'fiis.xlsx')
  print(f"All done! :)")

if __name__ == "__main__":
  main()