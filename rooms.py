import csv
import math

roomList = []

class Room():
    def __init__(self, roomNumber, bathroom, front, balc, balcNumber, rf):
        self.floor = math.floor(roomNumber/100)
        self.roomNumber = roomNumber
        self.bathroom = bathroom
        self.front = front
        self.balc = balc
        self.balcNumber = balcNumber
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
    clasificationPath = "dataLists/RoomClasifications.csv"
    def roomClean(string, ordered):
        if string == "":
                return False
        
        if ordered:
            return int(string)
        else:
            return True

    with open(clasificationPath) as file:
        reader = csv.DictReader(file)
        for row in reader:
            roomNumber = row["RoomNumber"]
            rf = row["RF"]
            bathroom = row["Bathroom"]
            front = row["Front"]
            balc = row["Balc"]
            frontBalcNumber = row["FrontBalcNumber"]

            roomNumber = roomClean(roomNumber, True)
            rf = roomClean(rf, False)
            bathroom = roomClean(bathroom, False)
            front = roomClean(front, False)
            balc = roomClean(balc, False)
            frontBalcNumber = roomClean(frontBalcNumber, True)

            newRoom = Room(roomNumber, bathroom, front, balc, frontBalcNumber, rf)
            roomList.append(newRoom)

def findRoom(rList, roomNumber):
    for room in rList:
        if room.roomNumber == roomNumber:
            return room
    
    return False

importRooms()