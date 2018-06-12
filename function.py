import contextlib
import math
import re
from smtplib import SMTP_SSL, SMTPAuthenticationError
from socket import gaierror
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from __init__ import Soup, url, max_orders

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

def get_items_on_page(page_no):
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

def get_items(url):
    count = 2
    endPage = get_end_page(Soup)
    print(endPage)
    items = {}
    i = endPage
    while i > 0:
        try:
            items_on_page = get_items_on_page(i)
            print("Sleeping for a 15 seconds...\n")
            time.sleep(15)
            i -= 1
        except Exception as e:
            print(e)
            print("Sleeping for a 90 seconds...\n")
            time.sleep(90)
            continue

        for id in items_on_page:
            items[id] = items_on_page[id]
        # put_items(items_on_page, count)
        count += len(items_on_page)
    return items

def put_items(sheet, items):
    items_array = []
    cell_range = sheet.range("A%d:E%d" % (1, len(items)))
    j = 0
    for i, id in enumerate(items.keys()):
        item = items[id]
        cell_range[j].value = id
        cell_range[j+1].value = item['name']
        cell_range[j+2].value = item['price']
        cell_range[j+3].value = item['link']
        cell_range[j+4].value = item['orders']
        j += 5
        #cell_range[i:i+len(item)] = [id, item['name'], item['price'], item['link'], item['orders']]

    sheet.update_cells(cell_range)
    # var column = source.getRange("D"+startRow+":D"+(startRow+keys.length-1));
    # column.setFormula('=HYPERLINK(D2:D, "link")');

def send_msg(items):
    #reply to thread or post an article in the newsgroup
    SMTPSVR = 'smtp.gmail.com'
    who = 'samchats333@gmail.com'
    msg = """
    From: Sam Chats <samchats333@gmail.com>
    To: Nate Schmidt <nws@nateschmidt.io>
    Subject: Hot items


    Hello Nat,
    Here are some interesting items:

    """
    """with open('message', 'w') as msg:
        msg.write('From: YOUR_NAME_HERE <blahBlah@blah.org>\n')
        msg.write('Newsgroups: %s\n' % group_name)
        msg.write('Subject: %s\n' % subject)
    subprocess.call(['nano', 'message'])"""

    recipients = ['parth1989shandilya@gmail.com']
    item_list = []

    for id in items:
        item_list.append("{name} - {link} - increased by {delta}".format(name=items[id]['name'], link=items[id]['link'], delta=items[id]['delta']))
    msg += '\n'.join(item_list)
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
    #sendSvr.starttls()
    try:
        sendSvr.login('samchats333@gmail.com', 'Parth@1989')
    except SMTPAuthenticationError:
        print("Invalid SMTP credentials.")
        exit()
    errs = sendSvr.sendmail(who, recipients, msg)
    sendSvr.quit()
    assert len(errs) == 0, errs
    print("Email sent!")