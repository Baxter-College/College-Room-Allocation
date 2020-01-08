NUMBER_OF_FLOORS = 7

# RULE #1: Balance the number of seniors on each floor
EQUALISE_SENIOR_INTERFLOOR_NUMBERS = True
# RULE #2: Balance the genders of a floor
EQUALISE_ONFLOOR_GENDER_BALANCE = True
GENDER_BALANCE_PERCENTAGE_LENIENCY = 0.25
# RULE #3: At least 1 of each gender in each sub-division
ALTERNATING_GENDERS_ROOM_SEPERATION = True
# RULE #8: At least 1 fresher in each sub-division
SUB_DIVISION_FRESHER_BALANCE = True
# RULE #4: Maximum number of seniors on shared balcs
NUMBER_OF_SENIORS_FRONT_BALC = 2
# RULE #5: Keep the number of males and females on a front balc equal
EQUALISE_ONBALC_GENDER_BALANCE = True
# RULE #6: Try to keep the number of senior males/females equal (I don't think this is nessacary)
EQUALISE_ONFLOOR_SENIOR_GENDER_BALANCE = True
# RULE #7: Allocate example freshers to rooms which are unavailable to seniors. NOTE: Unstable
ALLOCATE_EXAMPLE_FRESHERS = False


from rooms import getRoomFacts
import models
import math
import json

from datetime import datetime as dt


# floorNum is 1 indexed floor
def listAvailableRooms(floorNum, gender=None, isSenior = False):
    floor = models.Floor.findFloor(floorNum)
    if floor == None:
        return {}
    availableRooms = {}

    print(f"starting floor {floorNum} at {dt.now()}")
    floorSeniorCapacity = seniorCapacity(floorNum)
    # minus 1 to ignore RF room
    numOfRooms = floor.rooms.count() - 1
    seniorGenderCount = floor.numOfGender(isSenior=True)[gender]
    floorSeniorGenderCapacity = seniorCapacity(floorNum, gender)
    floorSeniorCount = floor.numOfSeniors
    totalGenderCount = floor.numOfGender()[gender]
    for room in floor.rooms.select().iterator():
        #cur = dt.now()
        roomNum = room.roomNumber
        roomFacts = getRoomFacts(roomNum)
        if (room.assigned):
            availableRooms[roomNum] = {"available":False, "reason":"Occupied", "roomFacts":roomFacts}
        else:
            availableRooms[roomNum] = {"available":True, "reason":"OK", "roomFacts":roomFacts}

            if room.rf == True:
                availableRooms[roomNum]["available"] = False
                availableRooms[roomNum]["reason"] = "RF room"
                continue
              
            if EQUALISE_SENIOR_INTERFLOOR_NUMBERS and isSenior:        
                if floorSeniorCount > floorSeniorCapacity:
                    availableRooms[roomNum]["available"] = False
                    availableRooms[roomNum]["reason"] = "Too many seniors on this floor. RULE #1"
                    continue

            if EQUALISE_ONFLOOR_SENIOR_GENDER_BALANCE and isSenior:
                if floorSeniorGenderCapacity >= seniorGenderCount)/floorSeniorGenderCapacity) < (0.5 - GENDER_BALANCE_PERCENTAGE_LENIENCY):
                    availableRooms[roomNum]["available"] = False
                    availableRooms[roomNum]["reason"] = "Too many seniors on this floor of your gender. RULE #6"
                    continue
            
            if EQUALISE_ONFLOOR_GENDER_BALANCE:
                
                if (totalGenderCount/numOfRooms) > (0.5 + GENDER_BALANCE_PERCENTAGE_LENIENCY):
                    availableRooms[roomNum]["available"] = False
                    availableRooms[roomNum]["reason"] = "Too many people on this floor of your gender. RULE #2"
                    continue

            divInfo = getDivisionInformation(floorNum, room.SubDivisionNumber)
            currGenderCount = 0
            if gender == 'm':
                currGenderCount = divInfo["numMale"]
            elif gender == 'f':
                currGenderCount = divInfo["numFemale"]

            if room.front and room.balc:
                if NUMBER_OF_SENIORS_FRONT_BALC <= divInfo["numSenior"] and isSenior:
                    availableRooms[roomNum]["available"] = False
                    availableRooms[roomNum]["reason"] = "Too many seniors on this balc. RULE #4"
                    continue
                
                if EQUALISE_ONBALC_GENDER_BALANCE:
                    if (divInfo["numOfRooms"] - currGenderCount)/divInfo["numOfRooms"] <= 0.5:
                        availableRooms[roomNum]["available"] = False
                        availableRooms[roomNum]["reason"] = "Too many people on this balc with your gender. RULE #5"
                        continue
            
            else:
                if ALTERNATING_GENDERS_ROOM_SEPERATION:
                    if ((divInfo["numOfRooms"] - currGenderCount)/divInfo["numOfRooms"] <= 0.25):
                        availableRooms[roomNum]["available"] = False
                        availableRooms[roomNum]["reason"] = "Too many people in this sub-divison. RULE #3"
                        continue
                
                if SUB_DIVISION_FRESHER_BALANCE:
                    if ((divInfo["numOfRooms"] - divInfo["numSenior"])/divInfo["numOfRooms"] <= 0.25):
                        availableRooms[roomNum]["available"] = False
                        availableRooms[roomNum]["reason"] = "Too many seniors in this sub-divison. RULE #8"
                        continue
        #print(f"room {roomNum} took {dt.now() - cur} time")
                
                
    outp = {}
    for key in availableRooms:
        outp[str(key)] = availableRooms[key]
    
    return outp

# the number of seniors that can fit on all floors evenly. if gender is included, will show the distrobution of the gender
def seniorCapacity(floorNum, gender=None):
    if (gender != None):
        numOfSeniors = models.Student.select().where(models.Student.year > 1).where(models.Student.gender == gender).count()
    else:
        numOfSeniors = models.Student.select().where(models.Student.year > 1).count()

    maxNumOfSeniors = math.ceil(numOfSeniors/7)
    
    # self.numOfSeniors-maxNumOfSeniors
    if maxNumOfSeniors == 0:
        return 1
    return maxNumOfSeniors

def getDivisionInformation(floorNum, division):

    divisionRooms = []
    numAvailable = 0
    numMale = 0
    numFemale = 0
    numSenior = 0
    numFresh = 0

    rooms = models.Room.select().where(models.Room.floor == floorNum).where(models.Room.SubDivisionNumber == division)

    for room in rooms.iterator():
        divisionRooms.append(room)

        if room.assigned == False:
            numAvailable += 1
        else:
            if models.Student.findFromRoom(room).gender == 'm':
                numMale += 1
            if models.Student.findFromRoom(room).gender == 'f':
                numFemale += 1
            if models.Student.findFromRoom(room).year > 1:
                numSenior += 1
            if models.Student.findFromRoom(room).year == 1:
                numFresh += 1

    numOfRooms = rooms.count()

    return {"numOfRooms":numOfRooms, "numAvailable":numAvailable, "numMale":numMale, "numFemale":numFemale, "numSenior":numSenior, "numFresh":numFresh}

# rturns string of current allocation
def currentRoomState():
    state = "Current state of all bookings:\n"
    for allocation in models.AllocatedRoom.select().iterator():
        state += f"{allocation.room} is allocated to {allocation.person}\n"
    return state

# Will return True if succsess, False if fail
# Takes zid and roomnum
def makeAllocation(zid, newRoomNum, subPreferences, extraInformation):
    student = models.Student.findStudent(zid)
    newRoom = models.Room.findRoom(newRoomNum)

    if student == None or newRoom == None:
        return False

    # Can overwrite if occupant is fresher
    if newRoom.assigned == True and newRoom.occupant.first().year > 1:
        return False
    
    models.AllocatedRoom.makeAllocation(zid, newRoomNum, json.dumps(subPreferences), currentRoomState(), extraInformation)

    if ALLOCATE_EXAMPLE_FRESHERS:
        pass
        # allocateFreshers()

    return True

def allocationsToCSV():
    rowList = [["Submission Time",
                "zID",
                "Allocation",
                "First Sub-Preference",
                "Second Sub-Preference",
                "Third Sub-Preference",
                "Fourth Sub-Preference",
                "Fifth Sub-Preference",
                "Submission Notes",
                "State When Submitted"]]
    
    for allocation in models.AllocatedRoom.select():
        subPreferences = json.loads(allocation.otherPreferences)
        row = [allocation.timeOfAllocation,
               allocation.person,
               allocation.room,
               subPreferences[0],
               subPreferences[1],
               subPreferences[2],
               subPreferences[3],
               subPreferences[4],
               allocation.extraInformation,
               allocation.currentState]
        
        rowList.append(row)
    return rowList