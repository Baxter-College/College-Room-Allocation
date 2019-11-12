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

def importRooms():
    
    # Cleans a string where an empty cell = False, ordered means a number, otherwise value is true
    def roomClean(string, ordered):
        if string == "":
                return False
        
        if ordered:
            return int(string)
        else:
            return True

    with open(ROOM_CLASSIFICATION_PATH) as file:
        reader = csv.DictReader(file)
        for row in reader:
            roomNumber = row["RoomNumber"]
            rf = row["RF"]
            bathroom = row["Bathroom"]
            front = row["Front"]
            balc = row["Balc"]
            SubDivisionNumber = row["SubDivisionNumber"]

            roomNumber = roomClean(roomNumber, True)
            rf = roomClean(rf, False)
            bathroom = roomClean(bathroom, False)
            front = roomClean(front, False)
            balc = roomClean(balc, False)
            SubDivisionNumber = roomClean(SubDivisionNumber, True)

            newRoom = Room(roomNumber, bathroom, front, balc, SubDivisionNumber, rf)
            roomList.append(newRoom)

def findRoom(rList, roomNumber):
    for room in rList:
        if room.roomNumber == roomNumber:
            return room
    
    return False

# takes safe room, returns string of facts about room
def getRoomFacts(room):
    details = ''
    if (room.bathroom):
        details += "Ensuite"
    
    if (room.balc):
        if (details != ''):
            details += ", "
        
        if (room.front):
            details += "front balc"
        else:
            details += "back balc"
    
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

importRooms()