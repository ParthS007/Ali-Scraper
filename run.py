import json
import os
import gspread
import function
from __init__ import url, credentials

#print(json.dumps(get_items(url), indent=4))
items = function.get_items(url)
file = gspread.authorize(credentials)

sheet_file = file.open("Ali_Express")
sheet = sheet_file.worksheet("Sheet1")
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}

function.put_items(sheet, items)
print("Done")
