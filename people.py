import datetime
import pytz
import models
from playhouse.shortcuts import model_to_dict
import json
import random
import string
import mail

def getStudentList():
    studentListData = {}
    studentList = models.Student.select().where(models.Student.year > 1)
    for student in studentList.iterator():
        timeString = student.startTime.strftime("%I:%M%p %d/%m/%Y")
        studentListData[student.zID] = {"gender":student.gender, "startDate":timeString}
    
    return studentListData

def import_students(reader):
    for row in reader:
        zid = row["zID"]
        # name = row["StudentName"]
        year = int(row["year"])
        room_points = int(row["roomPoints"])
        gender = row["gender"]
        password = row["password"]
        startTime = row["startTime"]
        ensuite = row["roomType"]

        if (ensuite == "ensuite"):
            ensuite = True
        else:
            ensuite = False

        if startTime == "":
            startTime = datetime.datetime.strptime("2050", "%Y")
        else:
            # in format "10:30AM 12/11/2019"
            tz = pytz.timezone("Australia/Sydney")
            startTime = datetime.datetime.strptime(startTime, "%I:%M%p %d/%m/%Y")
            tz.localize(startTime)

        models.Student.createStudent(zid, year, gender, ensuite, room_points, password, startTime)
    
    sysInfo = models.SystemInformation.getSysInfo()
    sysInfo.studentListUploaded = True
    sysInfo.save()

def checkPersonAllocated(zid):
    person = models.Student.findStudent(zid)
    
    if (person != None):
        if (person.assigned):
            return {"allocated":True, "room":person.allocation.get().room}
    
    return {"allocated":False, "room":False}

def personAllocatedList():
    allocatedList = {}
    for s in models.Student.select().iterator():
        allocatedList[s.zID] = checkPersonAllocated(s.zID)
    return allocatedList


def checkCorrectPassword(zid, password):
    person = models.Student.findStudent(zid)
    
    if (person != False):
        if (person.password == password):
            return True

    return False


def checkValidTime(zid):
    person = models.Student.findStudent(zid)
    time = datetime.datetime.now()
    # pytz.timezone("Australia/Sydney").localize(time)
    if (person != False):
        # # in format "10:30AM 12/11/2019"
        personStartTime = person.startTime
        pytz.timezone("Australia/Sydney").localize(personStartTime)
        # tz = pytz.timezone('Australia/Sydney')
        # startTime = datetime.datetime.strptime(startTime,"%I:%M%p %d/%m/%Y")
        # tz.localize(startTime)
        print(f"TIME COMPARE: person: {personStartTime}, now: {time}")
        if (personStartTime <= time):
            return True

            
    return False

def checkValidRoomType(zid, roomNum):
    person = models.Student.findStudent(zid)
    room = models.Room.findRoom(roomNum)

    if (person != False and room != False):
        if (person.hasEnsuite == room.bathroom):
            return True
    
    return False


def getStudentsByRoomPoints():
    studentList = models.Student.select().order_by(models.Student.roomPoints.desc())
    sterile = []
    for x in studentList.iterator():
        modelDict = model_to_dict(x)
        modelDict["startTime"] = str(modelDict["startTime"])
        sterile.append(modelDict)
    return sterile

def calculatePercentageAllocated():
    total = models.Student.select().count() # pylint: disable=no-value-for-parameter
    assigned = models.AllocatedRoom.select().count() # pylint: disable=no-value-for-parameter
    if (total == 0):
        return 0
    return (assigned/total * 100)

# takes a startTime string in format "10:30AM 12/11/2019"
def createAccessTimes(startTime, seperationMinutes=30):
    def addTime(currDate, addMinutes):
        dayStart = "09:00AM"
        dayEnd = "10:00PM"

        dayStart = pytz.timezone("Australia/Sydney").localize(datetime.datetime.strptime(dayStart, "%I:%M%p"))
        dayEnd = pytz.timezone("Australia/Sydney").localize(datetime.datetime.strptime(dayEnd, "%I:%M%p"))
        newTime = currDate + datetime.timedelta(minutes=addMinutes)
        
        if newTime.timetz() >= dayEnd.timetz():
            currDate += datetime.timedelta(days=1)
            currDate = currDate.replace(hour=dayStart.hour, minute=dayStart.minute)
            return currDate
        else:
            return newTime

    studentList = models.Student.select().order_by(models.Student.roomPoints.desc())
    tz = pytz.timezone("Australia/Sydney")
    newTime = datetime.datetime.strptime(startTime, "%Y-%m-%dT%H:%M")
    tz.localize(newTime)

    lastRoomPoints = studentList.get().roomPoints
    for s in studentList.iterator():
        if (s.roomPoints != lastRoomPoints):
            lastRoomPoints = s.roomPoints
            newTime = addTime(newTime, seperationMinutes)
        s.startTime = newTime
        s.save()
    
    sysInfo = models.SystemInformation.getSysInfo()
    sysInfo.startTimeSet = True
    sysInfo.save()

    # for s in studentList:
    #     print(s.zID,s.roomPoints,s.startTime)


def sendEmails(app):
    for s in models.Student.select():
        zid = s.zID
        password = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(8)])
        s.password = password
        s.save()
        startTime = s.startTime.strftime("%I:%M%p %d/%m/%Y")

        mail.sendEmail(app, f'{zid}@mailinator.com', password, startTime)
