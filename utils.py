import csv
import re
import pandas as pd


def normalize(value):
  if re.search("^(R\$)?\s*(\d+)\,(\d+)\s*$", value):
    return float(re.sub("^(R\$)?\s*(\d+)\,(\d+)\s*$", r"\2.\3", value))
  if re.search("^(R\$)?\s*(\d+)\,(\d+)\s*K\s*$", value):
    return float(re.sub("^^(R\$)?\s*(\d+)\,(\d+)\s*K\s*$", r"\2.\3", value)) * 1000
  if re.search("^(R\$)?\s*(\d+)\,(\d+)\s*M\s*$", value):
    return float(re.sub("^^(R\$)?\s*(\d+)\,(\d+)\s*M\s*$", r"\2.\3", value)) * 1000000
  if re.search("^(R\$)?\s*(\d+)\,(\d+)\s*B\s*$", value):
    return float(re.sub("^^(R\$)?\s*(\d+)\,(\d+)\s*B\s*$", r"\2.\3", value)) * 1000000000
  if re.search("^\s*\-?(\d+)\,(\d+)\s*%\s*$", value):
    return float(re.sub("^\s*\-?(\d+)\,(\d+)\s*%\s*$", r"\1.\2", value)) / 100
  return value


def export_to_csv(data, filename):
  fields = data[0].keys()
  with open(filename, 'w') as file:
    writer = csv.DictWriter(file, fieldnames = fields)
    writer.writeheader()
    writer.writerows(data)


def export_to_excel(data, filename):
  df = pd.DataFrame(data)
  df.to_excel(filename)
