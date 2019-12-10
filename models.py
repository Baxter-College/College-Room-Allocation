import os
from urllib.parse import urlparse
from peewee import *  # pylint: disable=unused-wildcard-import
import math
import datetime

# from dotenv import load_dotenv

# load_dotenv()
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
    import getpass
    username = getpass.getuser()
    if (username == "twright" or username == "tdcwr"):
        db = SqliteDatabase('test1.db')
    else:
        db_name = os.environ["DB_NAME"]
        db_user = os.environ["DB_USER"]
        db_pword = os.environ["DB_PASSWORD"]
        db = PostgresqlDatabase(db_name, user=db_user, password=db_pword)


class Base(Model):
    class Meta:
        database = db


class Floor(Base):
    floorNumber = IntegerField(primary_key=True)
    # rooms = FoorToRoom Model
    # numDivisions = IntegerField()

    @classmethod
    def createFloor(cls, floorNumber):
        try:
            newFloor = cls.create(
                floorNumber=floorNumber,
                # numDivisions=numOfDivisions
            )

            return newFloor
        except IntegrityError as e:
            print("insert error! ", e)
            raise ValueError("Floor Already Exists")

    @classmethod
    def findFloor(cls, floorNumber):
        found = cls.get_or_none(Floor.floorNumber == floorNumber)
        if found != None:
            return found
        else:
            return None

    @property
    def numOfSeniors(self):
        studentList = (
            Student.select()
            .join(AllocatedRoom)
            .join(Room)
            .where(Student.zID == AllocatedRoom.person)
            .where(AllocatedRoom.room == Room.roomNumber)
            .where(Room.floor == self.floorNumber)
            .where(Student.year > 1)
        )

        return studentList.count()

    @property
    def numOfFreshers(self):
        studentList = (
            Student.select()
            .join(AllocatedRoom)
            .join(Room)
            .where(Student.zID == AllocatedRoom.person)
            .where(AllocatedRoom.room == Room.roomNumber)
            .where(Room.floor == self.floorNumber)
            .where(Student.year == 1)
        )

        return studentList.count()

    def numOfGender(self, isSenior=False):
        maleCount = 0
        femaleCount = 0

        studentList = (
            Student.select()
            .join(AllocatedRoom)
            .join(Room)
            .where(Student.zID == AllocatedRoom.person)
            .where(AllocatedRoom.room == Room.roomNumber)
            .where(Room.floor == self.floorNumber)
        )

        for student in studentList:
            if isSenior and student.year == 1:
                continue

            if student.gender == "m":
                maleCount += 1
            if student.gender == "f":
                femaleCount += 1

        return {"m": maleCount, "f": femaleCount}


class Room(Base):
    roomNumber = IntegerField(primary_key=True)
    bathroom = BooleanField()
    rf = BooleanField()
    front = BooleanField()
    balc = BooleanField()
    SubDivisionNumber = IntegerField()
    floor = ForeignKeyField(Floor, backref="rooms")

    @classmethod
    def createRoom(cls, roomNum, bathroom, front, balc, rf, SubDivisionNumber):
        try:
            floorNum = math.floor(roomNum / 100)
            newRoom = cls.create(
                roomNumber=roomNum,
                bathroom=bathroom,
                front=front,
                balc=balc,
                rf=rf,
                SubDivisionNumber=SubDivisionNumber,
                floor=floorNum,
            )

            return newRoom
        except IntegrityError:
            raise ValueError("Room Already Exists")

    @classmethod
    def findRoom(cls, roomNumber):
        found = cls.get_or_none(Room.roomNumber == roomNumber)
        if found != None:
            return found
        else:
            return False
    
    @property
    def assigned(self):
        find = self.assignedTo
        if (find.count() == 0):
            return False
        else:
            return True
    
    @property
    def occupant(self):
        find = self.assignedTo
        if (find.count() == 0):
            return False
        else:
            return find.person


class Student(Base):
    zID = CharField(primary_key=True)
    # name = CharField()
    year = IntegerField()
    gender = CharField()
    roomPoints = IntegerField()
    password = CharField()
    startTime = DateTimeField(default=datetime.datetime.strptime("2050", "%Y"))

    @classmethod
    def createStudent(cls, zid, year, gender, roomPoints, password, startTime):
        try:
            newStudent = cls.create(
                zID=zid,
                # name=name,
                year=year,
                gender=gender,
                roomPoints=roomPoints,
                password=password,
                startTime=startTime,
            )

            return newStudent
        except IntegrityError:
            raise ValueError("Student Already Exists")

    @classmethod
    def findStudent(cls, zid):
        found = cls.get_or_none(Student.zID == zid)
        if found != None:
            return found
        else:
            return False
    
    @property
    def allocation(self):
        find = self.allocation
        if (find.count() == 0):
            return False
        else:
            return find.room

    @property
    def assigned(self):
        find = self.allocation
        if (find.count() == 0):
            return False
        else:
            return True

class AllocatedRoom(Base):
    timeOfAllocation = DateField(default=datetime.datetime.now())
    person = ForeignKeyField(Student, backref="allocation", unique=True)
    room = ForeignKeyField(Room, backref="assignedTo", unique=True)
    otherPreferences = TextField(null=True)

    @classmethod
    def makeAllocation(cls, zid, roomNumber, otherPreferences):
        try:
            newAllocation = cls.create(
                person = zid,
                room = roomNumber,
                otherPreferences = otherPreferences
            )

            return newAllocation
        except IntegrityError:
            raise ValueError("Allocation Already Exists")

def db_reset():
    db.connect()
    # db.drop_tables([Student, Floor, Room])
    db.create_tables([Student, Floor, Room, AllocatedRoom], safe=True)
    db.close()