from oauth2client.service_account import ServiceAccountCredentials

max_orders = 100
threshold = 5

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('ALI_Scraper-3.json', scope)

base_url = "https://www.aliexpress.com/wholesale?SortType=total_tranpro_desc"
