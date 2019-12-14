from peewee import SqliteDatabase, IntegerField, Model, DateTimeField, CharField, ForeignKeyField, BooleanField, fn
from datetime import datetime
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteDatabase('users.db', pragmas={'foreign_keys': 1})


# def time_format():
#     return datetime.now().strftime('%y.%m.%d %H:%M:%S.%f')[:-4]


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



db_2 = SqliteExtDatabase('my_app.db', pragmas=(
    ('cache_size', -1024 * 64),  # 64MB page-cache.
    ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
    ('foreign_keys', 1)),  regexp_function=True)  # Enforce foreign-key constraints. 


class Petition2(Model):
    class Meta:
        database = db_2
        db_table = "petition"

    petition_id = IntegerField()
    position_number = IntegerField()
    username = CharField()
    sign_date = CharField()
    

    def __str__(self):
        return f'{self.petition_id}: {self.position_number} {self.username} {self.sign_date}'






if __name__ == '__main__':
    db.create_tables([Petition], safe=True)
    db_2.create_tables([Petition2], safe=True)
    

    query = Petition.select()
    
    for i in range(200, 100000, 15):
        Petition2.create(
                petition_id = query.where(Petition.id==i)[0].petition_id,
                position_number = query.where(Petition.id==i)[0].position_number,
                username = query.where(Petition.id==i)[0].username,
                sign_date = query.where(Petition.id==i)[0].sign_date
            )
    
