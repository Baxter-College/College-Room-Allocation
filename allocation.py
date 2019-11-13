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


from people import studentList, Student, findPerson, NUM_OF_SENIORS, NUM_OF_FRESHERS
from rooms import roomList, Room, findRoom, getRoomFacts
import math
import csv
ALLOCATION_CSV_PATH = "dataLists/allocation.csv"
floorList = []

class Floor():
    def __init__(self, floorNumber, rooms, numDivisions):
        self.floorNumber = floorNumber
        self.rooms = rooms
        self.numDivisions = numDivisions

    @property
    def numOfSeniors(self):
        seniorCount = 0
        for room in self.rooms:
            if room.assigned == True:
                if room.occupant.year != 1:
                    seniorCount += 1
        
        return seniorCount

    @property
    def numOfFreshers(self):
        fresherCount = 0
        for room in self.rooms:
            if room.assigned == True:
                if room.occupant.year == 1:
                    fresherCount += 1
        
        return fresherCount

    # TODO: Deal with non-binary denominations
    def numOfGender(self, isSenior=False):
        maleCount = 0
        femaleCount = 0

        for room in self.rooms:
            if room.assigned == True:
                if isSenior and room.occupant.year == 1:
                    continue

                if room.occupant.gender == "m":
                    maleCount += 1
                if room.occupant.gender == "f":
                    femaleCount += 1
        
        return {"m":maleCount, "f":femaleCount}

# floorNum is 1 indexed floor
def listAvailableRooms(floorNum, gender=None, isSenior = False):
    floor = floorList[floorNum - 1]    
    availableRooms = {}

    for room in floor.rooms:
        if (room.assigned):
            availableRooms[room.roomNumber] = {"available":False, "reason":"Occupied", "roomFacts":getRoomFacts(room)}
        else:
            availableRooms[room.roomNumber] = {"available":True, "reason":"OK", "roomFacts":getRoomFacts(room)}
    
    floorSeniorCapacity = seniorCapacity(floorNum)
    
    # minus 1 to ignore RF room
    numOfRooms = len(floor.rooms) - 1

    if EQUALISE_SENIOR_INTERFLOOR_NUMBERS and isSenior:
        floorSeniorCount = floor.numOfSeniors
        if floorSeniorCount > floorSeniorCapacity:
            for room in availableRooms:
                if (availableRooms[room]["available"]):
                    availableRooms[room] = {"available":False, "reason":"Too many seniors on this floor. RULE #1", "roomFacts":getRoomFacts(room)}
            return availableRooms
    
    if EQUALISE_ONFLOOR_SENIOR_GENDER_BALANCE and isSenior:
        genderCount = floor.numOfGender(isSenior=True)[gender]


        if ((floorSeniorCapacity - genderCount)/floorSeniorCapacity) < (0.5 - GENDER_BALANCE_PERCENTAGE_LENIENCY):
            for room in availableRooms:
                if (availableRooms[room]["available"]):
                    availableRooms[room] = {"available":False, "reason":"Too many seniors on this floor of your gender. RULE #2", "roomFacts":getRoomFacts(room)}
            return availableRooms

    if EQUALISE_ONFLOOR_GENDER_BALANCE:
        genderCount = floor.numOfGender()[gender]
        
        
        if (genderCount/numOfRooms) > (0.5 + GENDER_BALANCE_PERCENTAGE_LENIENCY):
            for room in availableRooms:
                if (availableRooms[room]["available"]):
                    availableRooms[room] = {"available":False, "reason":"Too many people on this floor of your gender. RULE #3", "roomFacts":getRoomFacts(room)}
            return availableRooms


    for room in floor.rooms:
        if not room.assigned:
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
                if (ALTERNATING_GENDERS_ROOM_SEPERATION != 0):
                    surroundingCount = countAdjacentRooms(room, ALTERNATING_GENDERS_ROOM_SEPERATION)
                    if (surroundingCount[gender]/ALTERNATING_GENDERS_ROOM_SEPERATION > 0.5):
                        availableRooms[room.roomNumber] = {"available":False, "reason":"Trying to alternate rooms. RULE #3", "roomFacts":getRoomFacts(room)}
                        continue
    outp = {}
    for key in availableRooms:
        outp[str(key)] = availableRooms[key]
    
    return outp
                
# the number of seniors that can fit on all floors evenly
def seniorCapacity(floorNum):
    overflow = NUM_OF_SENIORS % 7
    if overflow != 0:
        
        # Distribute seniors to higher floors if there is not an even number
        if (overflow + floorNum) > 7:
            maxNumOfSeniors = math.floor(NUM_OF_SENIORS/7)+1
        else:
            maxNumOfSeniors = math.floor(NUM_OF_SENIORS/7)
    else:
        maxNumOfSeniors = NUM_OF_SENIORS/7
    
    # self.numOfSeniors-maxNumOfSeniors
    return maxNumOfSeniors

def getDivisionInformation(floorNum, division):
    floor = floorList[floorNum - 1]

    divisionRooms = []
    numAvailable = 0
    numMale = 0
    numFemale = 0
    numSenior = 0
    numFresh = 0

    for room in floor.rooms:
        if room.SubDivisionNumber == division:
            divisionRooms.append(room)

            if room.assigned == False:
                numAvailable += 1
            else:
                if room.occupant.gender == 'm':
                    numMale += 1
                if room.occupant.gender == 'f':
                    numFemale += 1
                if room.occupant.year > 1:
                    numSenior += 1
                if room.occupant.year == 1:
                    numFresh += 1

    numOfRooms = len(divisionRooms)

    return {"numOfRooms":numOfRooms, "numAvailable":numAvailable, "numMale":numMale, "numFemale":numFemale, "numSenior":numSenior, "numFresh":numFresh}

def allocateFreshers():
    unassignedMaleFreshers = []
    unassignedFemaleFreshers = []

    allValidMale = []
    allValidFemale = []

    for floor in range(NUMBER_OF_FLOORS):
        floorNum = floor + 1

        allValidMale.extend(listAvailableRooms(floorNum,"m",True))
        allValidFemale.extend(listAvailableRooms(floorNum,"f",True))


    for person in studentList:
        if person.year == 1:
            if person.assigned == False:
                if person.gender == 'm':
                    unassignedMaleFreshers.append(person)
                elif person.gender == 'f':
                    unassignedFemaleFreshers.append(person)

    for room in roomList:
        if room.rf == True:
            continue
        elif room not in allValidMale and room.assigned == False:
            makeAllocation(unassignedFemaleFreshers[0], room)
            unassignedFemaleFreshers.pop(0)
        elif room not in allValidFemale and room.assigned == False:
            makeAllocation(unassignedMaleFreshers[0], room)
            unassignedMaleFreshers.pop(0)


# Will return True if succsess, False if fail
def makeAllocation(student, newRoom):
    if type(student) == str:
        student = findPerson(studentList, student)
        if student == False:
            print ("ERROR: could not find student")

    if type(newRoom) == str or type(newRoom) == int:
        newRoom = findRoom(roomList, int(newRoom))
    
        if newRoom == False:
            print ("ERROR: could not find room")


    if student == False or newRoom == False:
        return False

    if newRoom.assigned == True and newRoom.occupant.year > 1:
        return False
    
    if student.assigned == True:
        oldRoom = student.allocation
        oldRoom.clearAllocation()
    
    newRoom.assignRoom(student)
    student.assignRoom(newRoom)

    if ALLOCATE_EXAMPLE_FRESHERS:
        allocateFreshers()

    updateAllocationCSV()
    return True

# returns dictionary {"m":#,"f":#} of the number of males and females around and including the room
def countAdjacentRooms(room, diameter):
    radius = (diameter - 1)/2
    numMale = 0
    numFemale = 0

    if ((room.roomNumber - radius) < room.floor.rooms[0].roomNumber):
        i = room.floor.rooms[0].roomNumber
        while (i <= room.roomNumber + radius):
            room = findRoom(room.floor.rooms, i)
            if (room.occupant.gender == "m"):
                numMale += 1
            elif (room.occupant.gender == "f"):
                numFemale += 1
    elif (room.roomNumber + radius > room.floor.rooms[-1].roomNumber):
        i = room.roomNumber - radius
        while (i <= room.floor.rooms[-1].roomNumber):
            room = findRoom(room.floor.rooms, i)
            if (room.occupant.gender == "m"):
                numMale += 1
            elif (room.occupant.gender == "f"):
                numFemale += 1
    else:
        i = room.roomNumber - radius
        while (i <= room.roomNumber + radius):
            room = findRoom(room.floor.rooms, i)
            if (room.occupant.gender == "m"):
                numMale += 1
            elif (room.occupant.gender == "f"):
                numFemale += 1
    
    return {"m":numMale, "f":numFemale}


def createFloors():
    def retDev(room):
        return room.SubDivisionNumber
    
    for floorNum in range(1,8):
        newList = []
        for room in roomList:
            if room.floor == floorNum:
                newList.append(room)
        numDivisions = max(newList, key=retDev)
        newFloor = Floor(floorNum, newList, numDivisions)
        floorList.append(newFloor)

# writes classes to CSVs
def updateAllocationCSV():
    includeEmptyRooms = False

    with open(ALLOCATION_CSV_PATH, 'w') as file:
        fieldNames = ["Floor","Room","zID","Occupied","Student Name","gender"]
        writer = csv.DictWriter(file, fieldnames=fieldNames)
        
        writer.writeheader()
        for room in roomList:
            if not includeEmptyRooms and room.assigned:
                writer.writerow({"Floor":room.floor,"Room":room.roomNumber,"Occupied":room.assigned,"zID":room.occupant.zID,"Student Name":room.occupant.name,"gender":room.occupant.gender})
            elif includeEmptyRooms:
                writer.writerow({"Floor":room.floor,"Room":room.roomNumber,"Occupied":room.assigned,"zID":room.occupant.zID,"Student Name":room.occupant.name,"gender":room.occupant.gender})

# reads CSVs and updates classes
def loadAllocatedCSV():
    with open(ALLOCATION_CSV_PATH) as file:
        reader = csv.DictReader(file)
        for row in reader:
            room = row["Room"]
            zID = row["zID"]

            makeAllocation(zID, room)
            

if __name__ == "__main__":
    createFloors()
    loadAllocatedCSV()

    for st in listAvailableRooms(6, 'm', True):
        print(f"{st.roomNumber} ",end='')
    print(f"\n")

    makeAllocation("z5293139",601)

    for st in listAvailableRooms(6, 'm', True):
        print(f"{st.roomNumber} ",end='')
    print(f"\n")



    makeAllocation("z5261721",602)

    for st in listAvailableRooms(6, 'f', True):
        print(f"{st.roomNumber} ",end='')
    print(f"\n")

        