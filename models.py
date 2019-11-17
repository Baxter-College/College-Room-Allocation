import os
from urllib.parse import urlparse
from peewee import *
import math


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

    @classmethod
    def createFloor(cls, floorNumber, numOfDivisions):
        try:
            newFloor = cls.create(
                floorNumber=floorNumber,
                numDivisions=numOfDivisions
            )

            return newFloor
        except IntegrityError:
            raise ValueError("Floor Already Exists")
    
    def numOfSeniors(self):
        studentList = (Student.select()
                            .join(Room)
                            .where(Student.allocation==Room.roomNum)
                            .where(Room.floorNum==self.floorNumber)
                            .where(Student.year>1))
        
        return studentList.count()

    def numOfFreshers(self):
        studentList = (Student.select()
                            .join(Room)
                            .where(Student.allocation==Room.roomNum)
                            .where(Room.floorNum==self.floorNumber)
                            .where(Student.year==1))
        
        return studentList.count()

    def numOfGender(self, isSenior=False):
        maleCount = 0
        femaleCount = 0

        studentList = (Student.select()
                            .join(Room)
                            .where(Student.allocation==Room.roomNum)
                            .where(Room.floorNum==self.floorNumber))

        for student in studentList:
            if isSenior and student.year == 1:
                continue

            if student.gender == "m":
                maleCount += 1
            if student.gender == "f":
                femaleCount += 1
        
        return {"m":maleCount, "f":femaleCount}

    

class Room(Base):
    roomNumber = IntegerField(primary_key=True)
    bathroom = BooleanField()
    front = BooleanField()
    balc = BooleanField()
    SubDivisionNumber = IntegerField()
    assigned = BooleanField()
    floor = ForeignKeyField(Floor, backref="rooms")

    @classmethod
    def createRoom(cls, roomNum, bathroom, front, balc, SubDivisionNumber):
        try:
            floorNum = math.floor(roomNum/100)
            newRoom = cls.create(
                roomNumber = roomNum,
                bathroom = bathroom,
                front = front,
                balc = balc,
                SubDivisionNumber = SubDivisionNumber,
                assigned = False,
                floor = floorNum
            )

            return newRoom
        except IntegrityError:
            raise ValueError("Room Already Exists")
    

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

    @classmethod
    def createStudent(cls, zid, name, year, gender, roomPoints, password, startTime):
        try:
            newStudent = cls.create(
                zID = zid,
                name = name,
                year = year,
                gender = gender,
                roomPoints = roomPoints,
                assigned = None,
                allocation = None,
                password = password,
                startTime = startTime
            )

            return newStudent
        except IntegrityError:
            raise ValueError("Student Already Exists")
    

class RoomPreferences(Base):
    pref_id = IntegerField(primary_key=True)
    preferanceNumber = IntegerField()
    student = ForeignKeyField(Student, backref="preferences")
    room = ForeignKeyField(Room, backref="studentSubPreferences")