import gspread

class GoogleSpreadSheetUtil:
  def __init__(self, sheet_name) -> None:
    sa = gspread.service_account(filename="service-account.json")
    sh = sa.open_by_key('1VwaHA58DtweRV2W_es9GMhUTho36odj0b18W0ajdgVc')
    self.wks = sh.worksheet(sheet_name)    

  def get_sheet_data(self):
    return self.wks.get_all_values()

  def find_cell(self, value):
    return self.wks.find(value)

  def update_cell(self, row, col, value):
    self.wks.update_cell(row, col, value)
