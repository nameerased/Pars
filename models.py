from peewee import SqliteDatabase, IntegerField, Model, DateTimeField, CharField, ForeignKeyField, BooleanField, fn
from datetime import datetime
import locale
from playhouse.sqlite_ext import SqliteExtDatabase
from peewee import chunked
import pymorphy2
from playhouse.migrate import *
import requests
from bs4 import BeautifulSoup
import json
import time


db = SqliteExtDatabase('petitions.db', pragmas=(
    ('cache_size', -1024 * 64),  # 64MB page-cache.
    ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
    ('foreign_keys', 1)), regexp_function=True)  # Enforce foreign-key constraints.


db_2 = SqliteExtDatabase('petitions__2.db', pragmas=(
    ('cache_size', -1024 * 64),  # 64MB page-cache.
    ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
    ('foreign_keys', 1)), regexp_function=True)  # Enforce foreign-key constraints.


class Petition(Model):
    class Meta:
        database = db
        db_table = "petition"

    petition_id = IntegerField(unique=True)
    status = BooleanField(null=True)
    title = TextField()
    article = TextField()
    answer = TextField(null=True)


class Petition_2(Model):
    class Meta:
        database = db_2
        db_table = "petition"

    petition_id = IntegerField(unique=True)
    status = BooleanField(null=True)
    title = TextField()
    article = TextField()
    answer = TextField(null=True)


class Vote(Model):
    class Meta:
        database = db
        db_table = "vote"

    petition = ForeignKeyField(Petition, field='petition_id')
    position_number = IntegerField()
    username = CharField(max_length=100)
    sign_date = DateField()
    gender = BooleanField(null=True)


class User(Model):
    class Meta:
        database = db_2
        db_table = "user"

    petition = ForeignKeyField(Petition_2, field='petition_id')
    position_number = IntegerField()
    username = CharField(max_length=100)
    sign_date = DateField()
    gender = BooleanField(null=True)


class Name(Model):
    class Meta:
        database = db
        db_table = "name"

    username = CharField(max_length=20, unique=True)
    gender = BooleanField(null=True)


class Name_2(Model):
    class Meta:
        database = db_2
        db_table = "name"

    username = CharField(max_length=20, unique=True)
    gender = BooleanField(null=True)


if __name__ == '__main__':
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    # db.create_tables([Petition], safe=True)

    # migrator = SqliteMigrator(db)
    # gender = BooleanField(null=True, default=None)
    # migrate(
    #     migrator.drop_column('Petition', 'gender'),
    #     migrator.add_column('Petition', 'gender', gender),
    # )

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    pass
