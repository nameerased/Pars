# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import requests
from models import Petition, db
import time
from peewee import chunked


# petitions = [53360, 55, 40, 53984, 215, 1606, 66, 48, 3354, 67062, 50271, 33, 12531, 1365, 42862, 57092, 5381, 63, 5147, 248, 53988, 7786, 176, 4504, 58280, 18957, 20993, 39, 319, 53544, 52270, 9785, 558, 2933, 50, 504, 18160, 208, 1799, 256, 52532, 44428, 10024, 35, 66668, 52500, 53772, 53416, 532, 49113, 4829, 36543, 1450, 52, 10961, 47048, 11459, 47294, 19983, 52152, 12582, 72]
petitions = []


def max_page(petition_url):
    html = requests.get(petition_url).text
    soup = BeautifulSoup(html, 'lxml')
    votes = int(soup.find('div', class_=re.compile(r'^petition_votes_txt$')).find('span').text)
    max_page = votes / 30 if votes % 30 == 0 else (votes // 30) + 1
    return int(max_page)


print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

for petition in petitions:
    data = []
    petition_url = 'https://petition.president.gov.ua/petition/' + str(petition)
    files = [petition_url + '/votes/' + str(i) for i in range(1, max_page(petition_url) + 1)]

    for file in files:
        html = requests.get(file).text
        soup = BeautifulSoup(html, 'lxml')
        rows = soup.find_all('div', class_=re.compile(r'^table_row$'))

        for r in rows:
            position_number = r.find('div', class_='table_cell number').string.replace('.', '')
            username = r.find('div', class_='table_cell name').string
            sign_date = r.find('div', class_='table_cell date').string

            data.append((petition, position_number, username, sign_date))

    print(petition, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    with db.atomic():
        # by default SQLite limits the number of bound variables in a SQL query to 999
        for batch in chunked(data, 200):
            Petition.insert_many(batch).execute()

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
