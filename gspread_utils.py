import gspread
import os
from dotenv import load_dotenv
load_dotenv()

class GoogleSpreadSheetUtil:
  def __init__(self, sheet_name) -> None:
    sa = gspread.service_account(filename=os.environ["SERVICE_ACCOUNT_FILE"])
    sh = sa.open_by_key(os.environ["SPREADSHEET_KEY"])
    self.wks = sh.worksheet(sheet_name)    

  def get_sheet_data(self):
    return self.wks.get_all_values()

  def find_cell(self, value):
    return self.wks.find(value)

  def update_cell(self, row, col, value):
    self.wks.update_cell(row, col, value)
