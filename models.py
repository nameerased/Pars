from peewee import SqliteDatabase, IntegerField, Model, DateTimeField, CharField, ForeignKeyField, BooleanField, fn
from datetime import datetime
from playhouse.sqlite_ext import SqliteExtDatabase
from peewee import chunked

# db_old = SqliteDatabase('users.db', pragmas={'foreign_keys': 1})
#
#
# def time_format():
#     return datetime.now().strftime('%y.%m.%d %H:%M:%S.%f')[:-4]
#
#
# class Petition_old(Model):
#     class Meta:
#         database = db_old
#         db_table = "petition"
#
#     petition_id = IntegerField()
#     position_number = IntegerField()
#     username = CharField()
#     sign_date = CharField()
#
#     def __str__(self):
#         return f'{self.petition_id}: {self.position_number} {self.username} {self.sign_date}'


db = SqliteExtDatabase('petitions.db', pragmas=(
    ('cache_size', -1024 * 64),  # 64MB page-cache.
    ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
    ('foreign_keys', 1)), regexp_function=True)  # Enforce foreign-key constraints.


class Petition(Model):
    class Meta:
        database = db
        db_table = "petition"

    petition_id = IntegerField()
    position_number = IntegerField()
    username = CharField()
    sign_date = CharField()

    def __str__(self):
        return f'{self.petition_id}: {self.position_number} {self.username} {self.sign_date}'


if __name__ == '__main__':
    # db_old.create_tables([Petition_old], safe=True)
    db.create_tables([Petition], safe=True)

    # query = Petition_old.select()
    #
    # # for n in range(0, 2200000, 100000):
    # data = []
    # for i in query[2200000 + 1:]:
    #     data.append(
    #         (i.petition_id, i.position_number, i.username, i.sign_date)
    #     )
    # print('append')
    # with db.atomic():
    #     # by default SQLite limits the number of bound variables in a SQL query to 999
    #     for batch in chunked(data, 990):
    #         Petition.insert_many(batch).execute()
