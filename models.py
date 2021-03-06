import os
from urllib.parse import urlparse
from peewee import *  # pylint: disable=unused-wildcard-import
import math
import datetime

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
    if (username == "twright" or username == "tdcwr" or username == "tomhill"):
        db = SqliteDatabase('test1.db')
    else:
        from dotenv import load_dotenv # pylint: disable=import-error
        load_dotenv()
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

        for student in studentList.iterator():
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
        except IntegrityError as e:
            raise ValueError(f"Room Already Exists {roomNum} : {e}")

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
    hasEnsuite = BooleanField(default=False)
    roomPoints = IntegerField()
    password = CharField()
    startTime = DateTimeField(default=datetime.datetime.strptime("2050", "%Y"))

    @classmethod
    def createStudent(cls, zid, year, gender, ensuite, roomPoints, password, startTime):
        try:
            newStudent = cls.create(
                zID=zid,
                # name=name,
                year=year,
                gender=gender,
                hasEnsuite=ensuite,
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

    @classmethod
    def findFromRoom(cls, roomNum):
        allocation = AllocatedRoom.get_or_none(AllocatedRoom.room == roomNum)
        if allocation != None:
            return allocation.person.get()
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
    timeOfAllocation = DateTimeField()
    person = ForeignKeyField(Student, backref="allocation", unique=True)
    room = ForeignKeyField(Room, backref="assignedTo", unique=True)
    otherPreferences = TextField(null=True)
    extraInformation = TextField(null=True)
    currentState = TextField()

    @classmethod
    def makeAllocation(cls, zid, roomNumber, otherPreferences, allocationState, extraInformation):
        try:
            newAllocation = cls.create(
                timeOfAllocation = datetime.datetime.now(),
                person = zid,
                room = roomNumber,
                otherPreferences = otherPreferences,
                currentState = allocationState,
                extraInformation = extraInformation
            )

            return newAllocation
        except IntegrityError:
            raise ValueError("Allocation Already Exists")

class SystemInformation(Base):
    startTimeSet = BooleanField(default=False)
    mailOutDone =  BooleanField(default=False)
    roomListUploaded = BooleanField(default=False)
    studentListUploaded =  BooleanField(default=False)
    systemIsRunning = BooleanField(default=True)
    

    @classmethod
    def getSysInfo(cls):
        return (cls.get_or_create())[0]

def dbWipe():
    modelList = [AllocatedRoom, Student, Room, Floor, SystemInformation]
    for model in modelList:
        model.delete().execute() # pylint: disable=no-value-for-parameter

def db_reset():
    db.connect()
    # db.drop_tables([Student, Floor, Room, AllocatedRoom, SystemInformation])
    db.create_tables([Student, Floor, Room, AllocatedRoom, SystemInformation], safe=True)
    db.close()