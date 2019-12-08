# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import re
import requests
import csv
import json

max_page = 834
petition_n = 73080
petition_url = 'https://petition.president.gov.ua/petition/' + str(petition_n)


while True:
    html = requests.get(petition_url + '/votes/' + str(max_page)).text
    soup = BeautifulSoup(html, 'lxml')
    founds = soup.find('div', class_=re.compile(r'^table$'))
    if founds:
        break
    else:
        max_page -= 1

files = [petition_url + '/votes/' + str(i) for i in range(1, max_page + 1)]

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

with open("output.csv", "w", newline='', encoding="cp1251", errors='ignore') as csv_file:
    writer = csv.writer(csv_file, delimiter=';')
    for key, val in user_dict.items():
        writer.writerow([key, val[0], val[1]])

with open('dict.json', 'w', encoding='utf-8') as json_file:
    json = json.dumps(user_dict, ensure_ascii=False)
    json_file.write(json)
