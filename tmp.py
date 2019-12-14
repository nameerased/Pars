# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import re
import requests
import csv
import json
from models import Petition
import time
from peewee import fn
from collections import Counter

# total rows
# total_rows = Petition_old.select().count()
# print('Total rows', total_rows)
total_rows = Petition.select().count()
print('Total rows', total_rows)


# petitions list
def petitions_list():
    petitions = Petition.select(Petition.petition_id).order_by(Petition.petition_id).distinct()
    petitions = [i.petition_id for i in petitions]
    return petitions


print('Len: ', len(petitions_list()))


# name contain substring
def name_contain(substring):
    query = Petition.select().where(Petition.username.regexp(substring))

    print(f'Found: {len(query)} with substring {substring}')
    show = int(input('Show (1), escape(0): '))
    if show:
        for i in query:
            print(f'{i.petition_id}: {i.username}')


name_contain(r'Дем.+янчук.+С')


# most frequent names
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


petitions_count()
