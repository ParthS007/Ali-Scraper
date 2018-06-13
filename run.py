import json
import os
import gspread
import function
from __init__ import credentials, max_orders, threshold



def main_search(sheet, query):
    last_row = function.next_available_row(sheet)
    prev_items_list = sheet.range("A2:H{last_row}".format(last_row=last_row))
    if last_row <= 2:
        print("New item to search: {item_name}".format(item_name=query))
        header = sheet.range("A1:H1")
        header[0] = "ID"
        header[1] = "Name"
        header[2] = "Price"
        header[3] = "Link"
        header[4] = "Orders"
        header[5] = "Previous Orders"
        header[6] = "Delta"
        header[7] = "Interesting"
        sheet.update_cells(header)
        prev_items_orders = {}
    else:
        prev_items_orders = function.range_to_items(prev_items_list)

    items = function.get_items(query)
    interesting = {}

    for id in items:
        prev_orders = prev_items_orders.get(id)
        if prev_orders is not None:
            items[id]['prev_orders'] = prev_orders
            items[id]['delta'] = items[id]['orders'] - items[id]['prev_orders']

            if items[id]['delta'] >= threshold and items[id]['prev_orders'] <= max_orders:
                interesting[id] = items[id]
                items[id]['interesting'] = True
            else:
                items[id]['interesting'] = False
        else:
            items[id]['prev_orders'] = None
            items[id]['delta'] = None
            items[id]['interesting'] = None  # new item!
    
    if interesting:
        function.send_msg(interesting, item_name=query)
    else:
        print("Nothing of interest [or new item added], mail not sent.")

    file = gspread.authorize(credentials)
    sheet_file = file.open("Ali_Express")
    sheet = sheet_file.worksheet(query)
    product_num_difference = len(prev_items_orders) - len(items)

    function.put_items(sheet, items, product_num_difference)
    print("Done for sheet {name}".format(sheet.title))


file = gspread.authorize(credentials)
sheet_file = file.open("Ali_Express")
sheets = sheet_file.worksheets()

for sheet in sheets:
    query = sheet.title
    print("Product: {query}".format(query=query))
    main_search(sheet, query)
