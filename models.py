import os
from urllib.parse import urlparse
from peewee import *


# TODO: add environ variables
if "HEROKU" in os.environ:
    url = urlparse(os.environ["DATABASE_URL"])
    db = PostgresqlDatabase(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
    )
else:
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_pword = os.environ["DB_PASSWORD"]
    db = PostgresqlDatabase(
        db_name,
        user=db_user,
        password=db_pword,
    )

class Base (Model):
    class Meta:
        database = db

class Floor(Base):
    floorNumber = IntegerField(primary_key=True)
    # rooms = FoorToRoom Model
    numDivisions = IntegerField()

    

class Room(Base):
    roomNumber = IntegerField(primary_key=True)
    bathroom = BooleanField()
    front = BooleanField()
    balc = BooleanField()
    SubDivisionNumber = IntegerField()
    assigned = BooleanField()
    floor = ForeignKeyField(Floor, backref="rooms")
    

class Student(Base):
    zID = CharField(primary_key=True)
    name = CharField()
    year = IntegerField()
    gender = CharField()
    roomPoints = IntegerField()
    assigned = BooleanField(null=True)
    allocation = ForeignKeyField(Room, backref="occupant", null=True)
    password = CharField()
    startTime = DateTimeField(default=datetime.datetime.strptime("2050","%Y"))
    

class RoomPreferences(Base):
    pref_id = IntegerField(primary_key=True)
    preferanceNumber = IntegerField()
    student = ForeignKeyField(Student, backref="preferences")
    room = ForeignKeyField(Room, backref="studentSubPreferences")