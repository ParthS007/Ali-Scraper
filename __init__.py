import contextlib
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS

import gspread
from oauth2client.service_account import ServiceAccountCredentials

max_orders = 100
threshold = 5

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('ALI_Scraper-3.json', scope)

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

product_name = "apple watch band"
base_url = "https://www.aliexpress.com/wholesale?SortType=total_tranpro_desc"
url = base_url + "&SearchText=" + "+".join(product_name.split(" "))

with contextlib.closing(urlopen(url)) as page:
    data = page.read()
Soup = BS(data, "lxml")
