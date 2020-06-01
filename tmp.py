# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import re
import requests
import csv
import json
from models import Petition, Name, Vote, db
import time
from peewee import fn, chunked
from collections import Counter


def get_html(url):
    r = requests.get(url)
    return r.text


# petitions list
def petitions_list():
    petitions = Petition.select(Petition.petition_id).order_by(Petition.petition_id).distinct()
    petitions = [i.petition_id for i in petitions]
    return petitions


# name contain substring
def name_contain(substring):
    query = Petition.select().where(Petition.username.regexp(substring))
    print(f'Found: {len(query)} with substring {substring}')
    show = int(input('Show (1), escape(0): '))
    if show:
        for i in query:
            print(f'{i.petition_id}: {i.username}')


# most frequent names
def most_frequent_names():
    query = (Petition
             .select(Petition.username, fn.COUNT(Petition.petition_id).alias('count'))
             .group_by(Petition.username)
             .order_by(fn.COUNT(Petition.petition_id).desc()))
    for row in query[:10]:
        print(row.username, row.count)


# count by petitions
def petitions_count():
    query = Petition.select(Petition.petition_id)
    petitions_list = [i.petition_id for i in query.distinct()]
    print(f'There is {len(petitions_list)} petitions in db')
    p_dict = dict()
    for i in petitions_list:
        p_dict[i] = query.where(Petition.petition_id == i).count()

    p_dict = {k: v for k, v in sorted(p_dict.items(), key=lambda item: item[1])}

    for i in p_dict.items():
        print(i)





def copy_db():
    # Name_2, Petition_2, User
    # db.drop_tables([Peticia], safe=True)
    # db.create_tables([Peticia], safe=True)


    # db.create_tables([Name], safe=True)
    # query = Name_2.select()
    # data = []
    # for i in query:
    #     data.append((i.username, i.gender))
    #
    # with db.atomic():
    #     # by default SQLite limits the number of bound variables in a SQL query to 999
    #     for batch in chunked(data, 450):
    #         Name.insert_many(batch, fields=[Name.username, Name.gender]).execute()
    #
    #
    #
    # db.create_tables([Petition], safe=True)
    # query = Petition_2.select()
    # for i in query:
    #     Petition.create(
    #         petition_id=i.petition_id,
    #         status=i.status,
    #         title=i.title,
    #         article=i.article,
    #         answer=i.answer
    #     )
    #
    #
    #
    db.create_tables([Vote], safe=True)
    for i in User.select(User.petition_id).distinct():
        data = []
        # p = Petition.get(petition_id=i.petition_id).petition_id
        p = i.petition_id
        query = User.select().where(User.petition == i.petition_id)

        for user in query:
            data.append((p, user.position_number, user.username, user.sign_date, user.gender))

        with db.atomic():
            # by default SQLite limits the number of bound variables in a SQL query to 999
            for batch in chunked(data, 198):
                # User.insert_many(batch, fields=[User.petition, User.position_number,
                #                                 User.username, User.sign_date, User.gender]).execute()
                Vote.insert_many(batch).execute()


if __name__ == '__main__':
    # print('Len: ', len(petitions_list()))
    # name_contain(r'Дем.денко.+Ант')
    # most_frequent_names()
    # petitions_count()
    # copy_db()
    # get_petition_info(53360)  # 53360 96180
    pass
