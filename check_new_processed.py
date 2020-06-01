# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import requests
from models import Petition, Name, Vote, db
import time
from peewee import chunked
from multiprocessing import Pool
import pymorphy2
from datetime import datetime
import locale
from main import max_page, set_gender, get_genders, parse_petition, get_html, get_petition_info

locale.setlocale(locale.LC_ALL, 'uk_UA')
m = pymorphy2.MorphAnalyzer(lang='uk')


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


def update_petitions(url):
    petitions_to_parse = []
    page_links = [f'{url}{i}' for i in range(1, 11)]
    petition_links = get_petition_links(page_links)
    first, second, third, fourth = 0, 0, 0, 0
    parsed_petitions = [int(i.split('/')[-1]) for i in petition_links]
    query_closed = Petition.select(Petition.petition_id).where(~Petition.status)
    closed = [i.petition_id for i in query_closed]
    petitions_to_check = set(parsed_petitions) - set(closed) - {45758}
    query_open = Petition.select(Petition.petition_id).where(Petition.status)
    open_ = [i.petition_id for i in query_open]

    for i in petitions_to_check:
        first += 1
        if i not in open_:
            second += 1
            print(i, 'not in db')
            petitions_to_parse.append(i)
            title, article, answer = get_petition_info(i)
            Petition.create(petition_id=i, title=title, article=article, answer=answer)
        else:
            third += 1
            count_in_db = Vote.select().where(Vote.petition_id == i).count()
            count = get_votes_count(f'https://petition.president.gov.ua/petition/{i}')
            if count - count_in_db > 1000:
                fourth += 1
                print(i, count_in_db, count)
                petitions_to_parse.append(i)
    print(first, second, third, fourth, sum((first, second, third, fourth)))
    return petitions_to_parse


# 93638 ukrbud

if __name__ == '__main__':
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    url = 'https://petition.president.gov.ua/archive?sort=votes&order=desc&page='
    petitions = update_petitions(url)
    parse_petition(petitions)
    # set_gender()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
