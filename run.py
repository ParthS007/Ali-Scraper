import json
import os
import gspread
import function
from __init__ import url, credentials, max_orders, threshold

file = gspread.authorize(credentials)
sheet_file = file.open("Ali_Express")
sheet = sheet_file.worksheet("Sheet1")
last_row = function.next_available_row(sheet)
prev_items_list = sheet.range("A2:H{last_row}".format(last_row=last_row))
prev_items_orders = function.range_to_items(prev_items_list)
items = function.get_items(url)
interesting = {}

for id in items:
    prev_orders = prev_items_orders.get(id)
    if prev_orders is not None:
        items[id]['prev_orders'] = prev_orders
        items[id]['delta'] = items[id]['orders'] - items[id]['prev_orders']

        if items[id]['delta'] > threshold and items[id]['prev_orders'] <= max_orders:
            interesting[id] = items[id]
            items[id]['interesting'] = True
        else:
            items[id]['interesting'] = False
    else:
        items[id]['prev_orders'] = None
        items[id]['delta'] = None
        items[id]['interesting'] = None  # new item!

function.send_msg(interesting)

file = gspread.authorize(credentials)
sheet_file = file.open("Ali_Express")
sheet = sheet_file.worksheet("Sheet1")
product_num_difference = len(prev_items_orders) - len(items)
function.put_items(sheet, items, product_num_difference)
print("Done")

# teamViewer chaalu rakh :)
# ok :+1
# hi
# hello
# 