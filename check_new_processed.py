# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import requests
from models import Petition, Name, db
import time
from peewee import chunked
from multiprocessing import Pool
import pymorphy2
from datetime import datetime
import locale

locale.setlocale(locale.LC_ALL, 'uk_UA')
m = pymorphy2.MorphAnalyzer(lang='uk')


def get_html(url):
    r = requests.get(url)
    return r.text


def get_max_page(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.find('ul', class_='pag_list').find('i', class_='fa fa-angle-right').parent.parent.previous
    return int(pages)


def get_votes_count(petition_url):
    html = requests.get(petition_url).text
    soup = BeautifulSoup(html, 'lxml')
    votes = int(soup.find('div', class_=re.compile(r'^petition_votes_txt$')).find('span').text)
    return votes


def get_page_links(url):
    page_links = []
    pages = get_max_page(url)
    for i in range(1, pages + 1):
        page_links.append(f'{url}{i}')
    return page_links


def get_petition_links(page_links):
    petition_links = []
    for link in page_links:
        html = get_html(link)
        soup = BeautifulSoup(html, 'lxml')
        a_s = soup.find_all('a', class_='pet_link')
        for a in a_s:
            pet_link = f"https://petition.president.gov.ua{a.get('href')}"
            petition_links.append(pet_link)
    return petition_links


def get_new(petition_links):
    new = []
    all_petitions = [int(i.split('/')[-1]) for i in petition_links]
    query = Petition.select(Petition.petition_id).distinct()
    petition_in_db = [i.petition_id for i in query]
    for i in all_petitions:
        if i not in petition_in_db:
            new.append(i)
    print()
    return new


def get_genders():
    genders = {}
    query = Name.select().where(Name.gender.is_null(False)).dicts()
    for i in query:
        genders[i['username']] = i['gender']
    print(len(genders))

    return genders


def set_gender():
    query = Petition.select().where(Petition.gender.is_null())
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
        Petition.bulk_update(data, fields=['gender'], batch_size=165)


def update_petitions(url):
    petitions_to_parse = []
    page_links = [f'{url}{i}' for i in range(1, 11)]
    petition_links = get_petition_links(page_links)
    first, second, third, fourth = 0, 0, 0, 0
    parsed_petitions = [int(i.split('/')[-1]) for i in petition_links]
    query_closed = Petition.select(Petition.petition_id).where(Petition.open == False).distinct()
    closed = [i.petition_id for i in query_closed]
    petitions_to_check = set(parsed_petitions) - set(closed) - {45758}
    query_open = Petition.select(Petition.petition_id).where(Petition.open == True).distinct()
    open_ = [i.petition_id for i in query_open]

    for i in petitions_to_check:
        first += 1
        if i not in open_:
            second += 1
            print(i, 'not in db')
            petitions_to_parse.append(i)
        else:
            third += 1
            count_in_db = Petition.select().where(Petition.petition_id == i).count()
            count = get_votes_count(f'https://petition.president.gov.ua/petition/{i}')
            if count - count_in_db > 1000:
                fourth += 1
                print(i, count_in_db, count)
                petitions_to_parse.append(i)
    print(first, second, third, fourth, sum((first, second, third, fourth)))
    return petitions_to_parse


def max_page(petition_url):
    html = requests.get(petition_url).text
    soup = BeautifulSoup(html, 'lxml')
    votes = int(soup.find('div', class_=re.compile(r'^petition_votes_txt$')).find('span').text)
    max_page = votes / 30 if votes % 30 == 0 else (votes // 30) + 1
    return int(max_page)


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

        if petitions:
            set_gender()
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


# 93638 ukrbud


url = 'https://petition.president.gov.ua/archive?sort=votes&order=desc&page='
print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
petitions = update_petitions(url)
parse_petition(petitions)
# set_gender()
print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
