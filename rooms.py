import models
import json

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

def makeAllocation(zid, room, subPreferences):
    room = models.Room.findRoom(room)
    room.assignRoom(zid)
    person = models.Student.findStudent(zid)
    person.otherPreferences = json.dumps(subPreferences)