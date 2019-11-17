import csv
import math

ROOM_CLASSIFICATION_PATH = "dataLists/RoomClasifications.csv"
roomList = []

class Room():
    def __init__(self, roomNumber, bathroom, front, balc, SubDivisionNumber, rf):
        self.floor = math.floor(roomNumber/100)
        self.roomNumber = roomNumber
        self.bathroom = bathroom
        self.front = front
        self.balc = balc
        self.SubDivisionNumber = SubDivisionNumber
        self.rf = rf
        self.assigned = False
        self.occupant = None

    # NOTE: This is an unsafe method, doesn't check if the person is already allocated
    def assignRoom(self, newOccupant):
        self.assigned = True
        self.occupant = newOccupant
    
    def clearAllocation(self):
        self.assigned = False
        self.occupant = None

    def __str__(self):
        return f"Room: {self.roomNumber}"

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

def findRoom(rList, roomNumber):
    for room in rList:
        if room.roomNumber == roomNumber:
            return room
    
    return False

# takes safe room, returns string of facts about room
def getRoomFacts(room):
    if (type(room) != Room):
        room = findRoom(roomList, room)
    
    details = ''
    if (room.bathroom):
        details += "Ensuite"
    
    if (room.balc):
        if (details != ''):
            details += ", "
        
        if (room.front):
            details += "Front balc"
        else:
            details += "Back balc"
    
    if (details != ''):
        details = "("+details+")"

    return details

def roomOccupied(roomNum):
    if (roomNum != ""):
        roomNum = int(roomNum)
        room = findRoom(roomList, roomNum)
        if (room != False):
            if (room.assigned):
                return {"occupied":True, "found":True}
            else:
                return {"occupied":False, "found":True}
        else:
            return {"occupied":True, "found":False}
    else:
        return {"occupied":True, "found":False}
