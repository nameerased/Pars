# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import re
import requests
import csv
import json
from models import Petition
import time

# petitions = [53360, 55, 40, 53984, 215, 1606, 66, 48, 3354, 67062, 50271, 33, 12531, 1365, 42862, 57092, 5381, 63, 5147, 248, 53988, 7786]
#  44428, 10024, 176, 4504, 58280, 18957, 20993, 39, 319, 53544, 52270, 9785
petitions = [208, 1799, 256, 558, 2933, 50, 504, 18160]
# petition_url = 'https://petition.president.gov.ua/petition/' + str(petition_n)
user_dict = dict()


def max_page(petition_url, ):
    html = requests.get(petition_url).text
    soup = BeautifulSoup(html, 'lxml')
    votes = int(soup.find('div', class_=re.compile(r'^petition_votes_txt$')).find('span').text)
    max_page = votes / 30 if votes % 30 == 0 else (votes // 30) + 1
    return int(max_page)

print(time.time())
for petition in petitions:
    user_dict[petition] = dict()
    petition_url = 'https://petition.president.gov.ua/petition/' + str(petition)
    files = [petition_url + '/votes/' + str(i) for i in range(1, max_page(petition_url) + 1)]

    for file in files:
        html = requests.get(file).text
        soup = BeautifulSoup(html, 'lxml')
        rows = soup.find_all('div', class_=re.compile(r'^table_row$'))

        for r in rows:
            number = r.find('div', class_='table_cell number').string.replace('.', '')
            name = r.find('div', class_='table_cell name').string
            date = r.find('div', class_='table_cell date').string

            user_dict[petition][int(number)] = [name, date]
    print(petition, time.time())

# with open("output.csv", "w", newline='', encoding="cp1251", errors='ignore') as csv_file:
#     writer = csv.writer(csv_file, delimiter=';')
#     for key, val in user_dict.items():
#         for k, v in val.items():
#             writer.writerow([key, k, v[0], v[1]])

# with open('dict.json', 'w', encoding='utf-8') as json_file:
#     json = json.dumps(user_dict, ensure_ascii=False)
#     json_file.write(json)

print(time.time())
for key, val in user_dict.items():
    for k, v in val.items():
        # writer.writerow([key, k, v[0], v[1]])
        Petition.create(
            petition_id = int(key),
            position_number = int(k),
            username = v[0],
            sign_date = v[1]
            )
print(time.time())