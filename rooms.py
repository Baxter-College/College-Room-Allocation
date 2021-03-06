import csv
import models
import math

def import_rooms(reader):
    for i in range(1,8):
        models.Floor.createFloor(i)
    for row in reader:
        roomNumber = int(row["RoomNumber"])
        rf = bool(row["RF"])
        bathroom = bool(row["Bathroom"])
        front = bool(row["Front"])
        balc = bool(row["Balc"])
        SubDivisionNumber = int(row["SubDivisionNumber"])

        models.Room.createRoom(roomNumber, bathroom, front, balc, rf, SubDivisionNumber)
    
    sysInfo = models.SystemInformation.getSysInfo()
    sysInfo.roomListUploaded = True
    sysInfo.save()

def basicImportRoom():
    with open("dataLists/RoomClasifications.csv") as file:
        reader = csv.DictReader(file)
        import_rooms(reader)

# takes safe room, returns string of facts about room
def getRoomFacts(room):
    foundRoom = models.Room.findRoom(room)
    
    details = ''
    if (foundRoom.bathroom):
        details += "Ensuite"
    
    if (foundRoom.balc):
        if (details != ''):
            details += ", "
        
        if (foundRoom.front):
            details += "front balc"
        else:
            details += "Back balc"
    
    if (details != ''):
        details = "("+details+")"

    return details

def roomOccupied(roomNum):
    if (roomNum != ""):
        roomNum = int(roomNum)
        room = models.Room.findRoom(roomNum)
        if (room != False):
            if (room.assigned):
                return {"occupied":True, "found":True}
            else:
                return {"occupied":False, "found":True}
        else:
            return {"occupied":True, "found":False}
    else:
        return {"occupied":True, "found":False}