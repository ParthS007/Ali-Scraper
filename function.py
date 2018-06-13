import contextlib
import math
import re
from smtplib import SMTP_SSL, SMTPAuthenticationError
from socket import gaierror
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
from __init__ import max_orders

price_patt = re.compile(r'.*\$(.*)')
orders_patt = re.compile(r'.*\((.*)\)')


def get_end_page(Soup):
    totalResult = Soup.find('strong', {'class': 'search-count'})
    results = int(totalResult.text.replace(',', ''))
    if (results >= 4800):
        endPage = 100
    elif ( results > 0 and results < 4800):
        endPage = math.ceil((results/4800))
    return endPage


def get_items_on_page(url, page_no):
    print("Page: " + str(page_no))
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}
    with contextlib.closing(urlopen(url+"&page="+str(page_no))) as page:
        data = page.read()
    soup = BS(data, "lxml")
    list_ele = soup.find('ul',{'id': 'hs-below-list-items'})
    items_ele = list_ele.find_all('div', {'class':'item'})
    items = {}

    for i, ele in enumerate(items_ele):
        info = ele.find('div', {'class': 'info'})
        link_ele = info.find('a', {'class': 'history-item'})
        link = link_ele['href']
        name = link_ele.text.strip()
        price_text = info.find('span', {'class': 'value'}).text
        price = price_patt.search(price_text).groups()[0]
        orders_ele = info.find('span', {'class': 'order-num'})
        orders_string = orders_ele.find('em').text
        orders_raw = orders_patt.search(
            orders_string
        ).groups()[0].replace(',', '')
        orders = int(orders_raw)
        tokens = link.split("?")[0].split("/")
        id = int(tokens[-1].split(".")[0])
        items[id] = {
            "name": name,
            "price": price,
            "link": link,
            "orders": orders
        }

    return items


def get_items(query):
    base_url = "https://www.aliexpress.com/wholesale?SortType=total_tranpro_desc"
    url = base_url + "&SearchText=" + "+".join(query.split(" "))
    count = 2

    with contextlib.closing(urlopen(url)) as page:
        data = page.read()
    Soup = BS(data, "lxml")
    endPage = get_end_page(Soup)
    items = {}
    i = endPage
    while i > 0:
        try:
            items_on_page = get_items_on_page(url, i)
            print("Sleeping for a 25 seconds...\n")
            time.sleep(25)
            i -= 1
        except Exception as e:
            print(e)
            print("Sleeping for a 150 seconds...\n")
            time.sleep(150)
            continue

        for id in items_on_page:
            items[id] = items_on_page[id]
        count += len(items_on_page)
    return items


def put_items(sheet, items, diff):
    items_array = []
    cell_range = sheet.range("A%d:H%d" % (2, len(items)+1))
    j = 0
    for i, id in enumerate(items.keys()):
        item = items[id]
        cell_range[j].value = id
        cell_range[j+1].value = item['name']
        cell_range[j+2].value = item['price']
        cell_range[j+3].value = item['link']
        cell_range[j+4].value = item['orders']
        cell_range[j+5].value = item['prev_orders']
        cell_range[j+6].value = item['delta']
        cell_range[j+7].value = item['interesting']
        j += 8
    if diff > 0:
        last_row = len(items) + 1
        blank_range = sheet.range("A%d:H%d" % (last_row+1, last_row+diff))
        for cell in blank_range:
            cell.value = None
        sheet.update_cells(blank_range)

    sheet.update_cells(cell_range)


def send_msg(items, item_name):
    #reply to thread or post an article in the newsgroup
    SMTPSVR = 'smtp.gmail.com'
    who = 'samchats333@gmail.com'
    msg = \
    """Subject: Hot items: {item_name}

    Hello Nat,
    Here are some interesting items:

    """.format(item_name=item_name)
    """with open('message', 'w') as msg:
        msg.write('From: YOUR_NAME_HERE <blahBlah@blah.org>\n')
        msg.write('Newsgroups: %s\n' % group_name)
        msg.write('Subject: %s\n' % subject)
    subprocess.call(['nano', 'message'])"""
    recipients = ['parth1989shandilya@gmail.com']
    item_list = []
    for id in items:
        item_list.append("{name} - {link} - increased by {delta} (From {prev_orders} to {orders})".format(name=items[id]['name'], link=items[id]['link'], delta=items[id]['delta'], prev_orders=items[id]['prev_orders'], orders=items[id]['orders']))
    msg += '\n\n'.join(item_list)
    msg += """

    Regards,
    SamChatsBot
    """
    try:
        sendSvr = SMTP_SSL(SMTPSVR, 465)
    except gaierror:
        print("Can't connect to %s." % SMTPSVR)
        exit()
    sendSvr.ehlo()
    try:
        sendSvr.login('samchats333@gmail.com', 'Parth@1989')
    except SMTPAuthenticationError:
        print("Invalid SMTP credentials.")
        exit()
    errs = sendSvr.sendmail(who, recipients, msg)
    sendSvr.quit()
    assert len(errs) == 0, errs
    print("Email sent!")


def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))  # fastest but perhaps stupid :)
    return len(str_list)


def range_to_items(items_range):
    matrix = [[] for _ in range(items_range[-1].row-1)]
    for cell in items_range:
        matrix[cell.row-2].append(cell)
    items_orders = {}
    for item_row in matrix:
        id = int(item_row[0].value)
        orders = int(item_row[4].value)
        items_orders[id] = orders
    return items_orders
