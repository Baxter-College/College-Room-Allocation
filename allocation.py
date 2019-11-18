NUMBER_OF_FLOORS = 7

# RULE #1: Balance the number of seniors on each floor
EQUALISE_SENIOR_INTERFLOOR_NUMBERS = True
# RULE #2: Balance the genders of a floor
EQUALISE_ONFLOOR_GENDER_BALANCE = True
GENDER_BALANCE_PERCENTAGE_LENIENCY = 0.1
# RULE #3: Equalises the number of males and females in a set of x rooms to try to alternate male and female. Odd numbers only, set to 0 to turn off
ALTERNATING_GENDERS_ROOM_SEPERATION = 0
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



# floorNum is 1 indexed floor
def listAvailableRooms(floorNum, gender=None, isSenior = False):
    floor = models.Floor.findFloor(floorNum)
    if floor == None:
        return {}
    availableRooms = {}

    for room in floor.rooms.select():
        if (room.assigned):
            availableRooms[room.roomNumber] = {"available":False, "reason":"Occupied", "roomFacts":getRoomFacts(room.roomNumber)}
        else:
            availableRooms[room.roomNumber] = {"available":True, "reason":"OK", "roomFacts":getRoomFacts(room.roomNumber)}
    
    floorSeniorCapacity = seniorCapacity(floorNum)
    
    # minus 1 to ignore RF room
    numOfRooms = floor.rooms.count() - 1

    if EQUALISE_SENIOR_INTERFLOOR_NUMBERS and isSenior:
        floorSeniorCount = floor.numOfSeniors
        if floorSeniorCount > floorSeniorCapacity:
            for room in availableRooms:
                if (availableRooms[room.roomNumber]["available"]):
                    availableRooms[room.roomNumber] = {"available":False, "reason":"Too many seniors on this floor. RULE #1", "roomFacts":getRoomFacts(room)}
            return availableRooms
    
    if EQUALISE_ONFLOOR_SENIOR_GENDER_BALANCE and isSenior:
        genderCount = floor.numOfGender(isSenior=True)[gender]


        if ((floorSeniorCapacity - genderCount)/floorSeniorCapacity) < (0.5 - GENDER_BALANCE_PERCENTAGE_LENIENCY):
            for room in availableRooms:
                if (availableRooms[room.roomNumber]["available"]):
                    availableRooms[room.roomNumber] = {"available":False, "reason":"Too many seniors on this floor of your gender. RULE #2", "roomFacts":getRoomFacts(room)}
            return availableRooms

    if EQUALISE_ONFLOOR_GENDER_BALANCE:
        genderCount = floor.numOfGender()[gender]
        
        
        if (genderCount/numOfRooms) > (0.5 + GENDER_BALANCE_PERCENTAGE_LENIENCY):
            for room in availableRooms:
                if (availableRooms[room.roomNumber]["available"]):
                    availableRooms[room.roomNumber] = {"available":False, "reason":"Too many people on this floor of your gender. RULE #3", "roomFacts":getRoomFacts(room)}
            return availableRooms

    roomList = models.Room.select().where(models.Room.assigned==False).where(models.Room.floor == floorNum)

    for room in roomList:
        if room.rf:
            availableRooms[room.roomNumber] = {"available":False, "reason":"RF room", "roomFacts":getRoomFacts(room)}
            continue
        
        if room.front and room.balc:
            divInfo = getDivisionInformation(floorNum, room.SubDivisionNumber)
            
            if NUMBER_OF_SENIORS_FRONT_BALC <= divInfo["numSenior"] and isSenior:
                availableRooms[room.roomNumber] = {"available":False, "reason":"Too many seniors on this balc. RULE #4", "roomFacts":getRoomFacts(room)}
                continue
            
            if EQUALISE_ONBALC_GENDER_BALANCE:
                currGenderCount = 0
                if gender == 'm':
                    currGenderCount = divInfo["numMale"]
                elif gender == 'f':
                    currGenderCount = divInfo["numFemale"]

                if (divInfo["numOfRooms"] - currGenderCount)/divInfo["numOfRooms"] <= 0.5:
                    availableRooms[room.roomNumber] = {"available":False, "reason":"Too many people on this balc with your gener. RULE #5", "roomFacts":getRoomFacts(room)}
                    continue
            
            
        else:
            # DEBUG: need to change alternating genders to subdevision
            if (ALTERNATING_GENDERS_ROOM_SEPERATION != 0):
                pass
                # surroundingCount = countAdjacentRooms(room, ALTERNATING_GENDERS_ROOM_SEPERATION)
                # if (surroundingCount[gender]/ALTERNATING_GENDERS_ROOM_SEPERATION > 0.5):
                #     availableRooms[room.roomNumber] = {"available":False, "reason":"Trying to alternate rooms. RULE #3"}
                #     continue
    outp = {}
    for key in availableRooms:
        outp[str(key)] = availableRooms[key]
    
    return outp
                
# the number of seniors that can fit on all floors evenly
def seniorCapacity(floorNum):
    numOfSeniors = models.Student.select().where(models.Student.year > 1).count()
    overflow = numOfSeniors % 7
    if overflow != 0:
        
        # Distribute seniors to higher floors if there is not an even number
        if (overflow + floorNum) > 7:
            maxNumOfSeniors = math.floor(numOfSeniors/7)+1
        else:
            maxNumOfSeniors = math.floor(numOfSeniors/7)
    else:
        maxNumOfSeniors = numOfSeniors/7
    
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

    for room in models.Room.select().where(models.Room.floor == floorNum).where(models.Room.SubDivisionNumber == division):
        divisionRooms.append(room)

        if room.assigned == False:
            numAvailable += 1
        else:
            if room.occupant.first().gender == 'm':
                numMale += 1
            if room.occupant.first().gender == 'f':
                numFemale += 1
            if room.occupant.first().year > 1:
                numSenior += 1
            if room.occupant.first().year == 1:
                numFresh += 1

    numOfRooms = len(divisionRooms)

    return {"numOfRooms":numOfRooms, "numAvailable":numAvailable, "numMale":numMale, "numFemale":numFemale, "numSenior":numSenior, "numFresh":numFresh}

# TODO: complete this with peewee
# def allocateFreshers():
#     unassignedMaleFreshers = []
#     unassignedFemaleFreshers = []

#     allValidMale = []
#     allValidFemale = []

#     for floor in range(NUMBER_OF_FLOORS):
#         floorNum = floor + 1

#         allValidMale.extend(listAvailableRooms(floorNum,"m",True))
#         allValidFemale.extend(listAvailableRooms(floorNum,"f",True))


#     for person in studentList:
#         if person.year == 1:
#             if person.assigned == False:
#                 if person.gender == 'm':
#                     unassignedMaleFreshers.append(person)
#                 elif person.gender == 'f':
#                     unassignedFemaleFreshers.append(person)

#     for room in models.Room.select():
#         if room.rf == True:
#             continue
#         elif room not in allValidMale and room.assigned == False:
#             makeAllocation(unassignedFemaleFreshers[0], room)
#             unassignedFemaleFreshers.pop(0)
#         elif room not in allValidFemale and room.assigned == False:
#             makeAllocation(unassignedMaleFreshers[0], room)
#             unassignedMaleFreshers.pop(0)


# Will return True if succsess, False if fail
# Takes zid and roomnum
def makeAllocation(zid, newRoomNum):
    student = models.Student.findStudent(zid)
    newRoom = models.Room.findRoom(newRoomNum)

    if student == None or newRoom == None:
        return False

    # Can overwrite if occupant is fresher
    if newRoom.assigned == True and newRoom.occupant.first().year > 1:
        return False
    
    if student.assigned == True:
        oldRoom = student.allocation
        oldRoom.clearAllocation()
    
    newRoom.assignRoom(zid)

    if ALLOCATE_EXAMPLE_FRESHERS:
        pass
        # allocateFreshers()

    return True