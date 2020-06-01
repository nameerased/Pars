# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import requests
from models import Petition, db
import time
from peewee import chunked
from multiprocessing import Pool
import pymorphy2
from main import max_page


petitions = [53988]  # 35413


# def max_page(petition_url):
#     html = requests.get(petition_url).text
#     soup = BeautifulSoup(html, 'lxml')
#     votes = int(soup.find('div', class_=re.compile(r'^petition_votes_txt$')).find('span').text)
#     max_page = votes / 30 if votes % 30 == 0 else (votes // 30) + 1
#     return int(max_page)


def get_all_links(petition):
    petition_url = 'https://petition.president.gov.ua/petition/' + str(petition)
    all_links = [petition_url + '/votes/' + str(i) for i in range(1, max_page(petition_url) + 1)]
    print(len(all_links))
    return all_links


# print(len(get_all_links(petitions[0])))
# print(get_all_links(petitions[0])[:5])


# for file in get_all_links(petitions[0]):
#     data = []
#     html = requests.get(file).text
#     soup = BeautifulSoup(html, 'lxml')
#     rows = soup.find_all('div', class_=re.compile(r'^table_row$'))

#     for r in rows:
#         position_number = r.find('div', class_='table_cell number').string.replace('.', '')
#         username = r.find('div', class_='table_cell name').string
#         sign_date = r.find('div', class_='table_cell date').string

#         data.append((petitions, position_number, username, sign_date))


def make_all(link):
    data = []
    html = requests.get(link).text
    soup = BeautifulSoup(html, 'lxml')
    rows = soup.find_all('div', class_=re.compile(r'^table_row$'))
    
    for r in rows:
        position_number = r.find('div', class_='table_cell number').string.replace('.', '')
        username = r.find('div', class_='table_cell name').string
        sign_date = r.find('div', class_='table_cell date').string
        
        data.append((petitions, position_number, username, sign_date))

    # with db.atomic():
    #     # by default SQLite limits the number of bound variables in a SQL query to 999
    #     for batch in chunked(data, 200):
    #         Petition.insert_many(batch).execute()


print(petitions, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

# with db.atomic():
#     # by default SQLite limits the number of bound variables in a SQL query to 999
#     for batch in chunked(data, 200):
#         Petition.insert_many(batch).execute()

# print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

if __name__ == '__main__':
    with Pool(3) as p:
        p.map(make_all, get_all_links(petitions[0]))
