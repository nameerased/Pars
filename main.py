# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import re
import requests
import csv
import json

petition_n = 73080
petition_url = 'https://petition.president.gov.ua/petition/' + str(petition_n)
files = [petition_url + '/votes/' + str(i) for i in range(1, 644)]

page_count = 'users-table-pag'


# files_dir = os.path.join('htmls', '73080')
# files = [f for f in os.listdir(files_dir) if f.endswith('.html')]
user_dict = dict()


for file in files:
    html = requests.get(file).text
    soup = BeautifulSoup(html, 'lxml')
    rows = soup.find_all('div', class_=re.compile(r'^table_row$'))

    for r in rows:
        number = r.find('div', class_='table_cell number').string.replace('.', '')
        name = r.find('div', class_='table_cell name').string
        date = r.find('div', class_='table_cell date').string

        # print(number, name, date)
        user_dict[int(number)] = [name, date]

print(user_dict)
# for i in range(1, 500):
#     print(i, user_dict[i])

w = csv.writer(open("output.csv", "w", encoding="utf8"))
for key, val in user_dict.items():
    w.writerow([key, val[0], val[1]])

json = json.dumps(user_dict)
