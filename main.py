# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import re
import requests
import csv
import json


# petition_n = 53360
petitions = [53360, 55, 40, 53984, 215]
# petition_url = 'https://petition.president.gov.ua/petition/' + str(petition_n)
user_dict = dict()


def max_page(petition_url, ):
    html = requests.get(petition_url).text
    soup = BeautifulSoup(html, 'lxml')
    votes = soup.find('div', class_=re.compile(r'^petition_votes_txt$')).find('span').text
    max_page = int(votes) / 30 if int(votes) % 30 == 0 else (int(votes) // 30) + 1
    return max_page


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
    print(petition)

with open("output.csv", "w", newline='', encoding="cp1251", errors='ignore') as csv_file:
    writer = csv.writer(csv_file, delimiter=';')
    for key, val in user_dict.items():
        for k, v in val.items():
            writer.writerow([key, k, v[0], v[1]])

# with open('dict.json', 'w', encoding='utf-8') as json_file:
#     json = json.dumps(user_dict, ensure_ascii=False)
#     json_file.write(json)
