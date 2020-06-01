# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import requests
from models import Petition, db, Name, Vote
import time
from peewee import chunked
import pymorphy2
import locale
from datetime import datetime

locale.setlocale(locale.LC_ALL, 'uk_UA')
m = pymorphy2.MorphAnalyzer(lang='uk')


def get_html(url):
    r = requests.get(url)
    return r.text


def max_page(petition_url):
    html = get_html(petition_url)
    soup = BeautifulSoup(html, 'lxml')
    votes = int(soup.find('div', class_=re.compile(r'^petition_votes_txt$')).find('span').text)
    max_page = votes / 30 if votes % 30 == 0 else (votes // 30) + 1
    return int(max_page)


def get_genders():
    genders = {}
    query = Name.select().where(Name.gender.is_null(False)).dicts()
    for i in query:
        genders[i['username']] = i['gender']
    print(len(genders))

    return genders


def set_gender():
    query = Vote.select().where(Vote.gender.is_null())
    query_genders = get_genders()
    data = []
    for i in query:
        try:
            name = " ".join(i.username.split()).split(' ')[1]
        except IndexError:
            name = " ".join(i.username.split()).split(' ')[0]
        gender = query_genders.get(name, None)

        if gender is not None:
            if gender:
                i.gender = True
                data.append(i)
            elif not gender:
                i.gender = False
                data.append(i)
    with db.atomic():
        Vote.bulk_update(data, fields=['gender'], batch_size=165)


def get_petition_info(petition_n):
    petition_url = 'https://petition.president.gov.ua/petition/' + str(petition_n)
    html = get_html(petition_url)
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find('div', class_='page_left col-xs-8').find('h1').text
    article = soup.find('div', class_='article').text.strip()
    answer = soup.find('div', id='pet-tab-2').text.strip()
    answer = answer if answer else None
    return title, article, answer


def get_petition_status(petition_n):
    petition_url = 'https://petition.president.gov.ua/petition/' + str(petition_n)
    html = get_html(petition_url)
    soup = BeautifulSoup(html, 'lxml')
    status = soup.find('div', class_='votes_progress_label').find('span')
    return False if status else True


def parse_petition(petitions):
    for petition in petitions:
        # get_petition_status(petition)
        data = []
        petition_url = 'https://petition.president.gov.ua/petition/' + str(petition)
        pages = [petition_url + '/votes/' + str(i) for i in range(1, max_page(petition_url) + 1)]

        for page in pages:
            html = requests.get(page).text
            soup = BeautifulSoup(html, 'lxml')
            rows = soup.find_all('div', class_=re.compile(r'^table_row$'))

            for r in rows:
                position_number = r.find('div', class_='table_cell number').string.replace('.', '')
                username = r.find('div', class_='table_cell name').string
                day, month, year = r.find('div', class_='table_cell date').string.split(' ')
                new_month = m.parse(month)[0].inflect({'nomn'}).word.title()
                sign_date = datetime.strptime(' '.join([day, new_month, year]), '%d %B %Y')

                data.append((petition, position_number, username, sign_date))

        if Vote.select().where(Vote.petition == petition):
            print(f'petition {petition} was in db with',
                  Vote.delete().where(Vote.petition == petition).execute(), 'rows')
        with db.atomic():
            # by default SQLite limits the number of bound variables in a SQL query to 999
            for batch in chunked(data, 249):
                Vote.insert_many(batch, fields=['petition', 'position_number', 'username', 'sign_date']).execute()

        status = get_petition_status(petition)
        Petition.update(status=status).where(Petition.petition_id == petition).execute()
    if petitions:
        set_gender()


if __name__ == '__main__':
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    petitions = [92038, 93638]  # 93638 ukrbud
    parse_petition(petitions)
    set_gender()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
