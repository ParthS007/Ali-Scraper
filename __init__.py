import contextlib
import json
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('ALI_Scraper-3.json', scope)

#credentials = ServiceAccountCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
"""file = gspread.authorize(credentials)

sheet_file = file.open("Ali_Express")
sheet = sheet_file.worksheet("Sheet1")
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}
"""
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

max_orders = 100
product_name = "apple watch band"
base_url = "https://www.aliexpress.com/wholesale?SortType=total_tranpro_desc"
url = base_url + "&SearchText=" + "+".join(product_name.split(" "))

#site = requests.get(url, headers)
"""driver = webdriver.PhantomJS()
driver.set_window_size(1120, 500)
driver.get(url)
body = WebDriverWait(driver, 10).until(EC.presence_of_element_located(((By.TAG_NAME, "body"))))
data = body.get_attribute("innerHTML")
print(data)"""
with contextlib.closing(urlopen(url)) as page:
    data = page.read()
print(data)
Soup = BS(data, "lxml")
#Soup = BS(data, 'lxml')
