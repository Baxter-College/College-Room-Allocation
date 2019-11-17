import datetime
import pytz
import models


def getStudentList():
    studentListGender = {}
    studentList = models.Student.select().where(models.Student.year > 1)
    
    for student in studentList:
        studentListGender[student.zID] = student.gender
    
    return studentListGender



def checkPersonAllocated(zid):
    person = models.Student.findStudent(zid)
    
    if (person != None):
        if (person.assigned):
            return {"allocated":True, "room":person.allocation}
    
    return {"allocated":False, "room":False}

def checkCorrectPassword(zid, password):
    person = models.Student.findStudent(zid)
    
    if (person != None):
        if (person.password == password):
            return True

    return False


def checkValidTime(zid, time):
    person = models.Student.findStudent(zid)

    if (person != False):
        # # in format "10:30AM 12/11/2019"
        # tz = pytz.timezone('Australia/Sydney')
        # startTime = datetime.datetime.strptime(startTime,"%I:%M%p %d/%m/%Y")
        # tz.localize(startTime)
        if (person.startTime <= time):
            return True

            
    return False
