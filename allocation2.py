NUMBER_OF_FLOORS = 7


from people import studentList, Student, findPerson, NUM_OF_SENIORS, NUM_OF_FRESHERS
from rooms import roomList, Room, findRoom
import math
import csv
floorList = []

class Floor():
    def __init__(self, floorNumber, rooms):
        self.floorNumber = floorNumber
        self.rooms = rooms





def createFloors():
    for floorNum in range(1,8):
        newList = []
        for room in roomList:
            if room.floor == floorNum:
                newList.append(room)
        
        newFloor = Floor(floorNum, newList)
        floorList.append(newFloor)