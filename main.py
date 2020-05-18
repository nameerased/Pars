# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import requests
from models import Petition, db, Name
import time
from peewee import chunked
import pymorphy2
import locale
from datetime import datetime


def max_page(petition_url):
    html = requests.get(petition_url).text
    soup = BeautifulSoup(html, 'lxml')
    votes = int(soup.find('div', class_=re.compile(r'^petition_votes_txt$')).find('span').text)
    max_page = votes / 30 if votes % 30 == 0 else (votes // 30) + 1
    return int(max_page)


# print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

locale.setlocale(locale.LC_ALL, 'uk_UA')
m = pymorphy2.MorphAnalyzer(lang='uk')


def parse_petition(petitions):
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
                day, month, year = r.find('div', class_='table_cell date').string.split(' ')
                new_month = m.parse(month)[0].inflect({'nomn'}).word.title()
                sign_date = datetime.strptime(' '.join([day, new_month, year]), '%d %B %Y')

                data.append((petition, position_number, username, sign_date))

        print(petition, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

        if Petition.select().where(Petition.petition_id == petition):
            print(f'petition {petition} was in db with',
                  Petition.delete().where(Petition.petition_id == petition).execute(), 'rows')
        with db.atomic():
            # by default SQLite limits the number of bound variables in a SQL query to 999
            for batch in chunked(data, 165):
                Petition.insert_many(batch, fields=[Petition.petition_id, Petition.position_number, Petition.username,
                                                    Petition.sign_date]).execute()

        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


petitions = [93638, 92038]  # 93638 ukrbud

parse_petition(petitions)
