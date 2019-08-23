NUMBER_OF_FLOORS = 7

# Balance the number of seniors on each floor
EQUALISE_SENIOR_INTERFLOOR_NUMBERS = True
# Balance the genders of a floor
EQUALISE_ONFLOOR_GENDER_BALANCE = True
GENDER_BALANCE_PERCENTAGE_LENIENCY = 0.1
# Maximum number of seniors on shared balcs
NUMBER_OF_SENIORS_FRONT_BALC = 2
# Keep the number of males and females on a front balc equal
EQUALISE_ONBALC_GENDER_BALANCE = True
# Try to keep the number of senior males/females equal (I don't think this is nessacary)
EQUALISE_ONFLOOR_SENIOR_GENDER_BALANCE = True

# TODO: Discuss what this code will do: if people know they will get a bad room, will they actually come back?

from people import studentList, Student, findPerson, NUM_OF_SENIORS, NUM_OF_FRESHERS
from rooms import roomList, Room, findRoom
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

def listAvaliableRooms(floorNum, gender=None, isSenior = False):
    floor = floorList[floorNum - 1]    
    avaliableRooms = []
    
    floorSeniorCapacity = seniorCapacity(floorNum)
    numOfRooms = len(floor.rooms)

    if EQUALISE_SENIOR_INTERFLOOR_NUMBERS and isSenior:
        floorSeniorCount = floor.numOfSeniors

        if floorSeniorCount > floorSeniorCapacity:
            return avaliableRooms
    
    if EQUALISE_ONFLOOR_SENIOR_GENDER_BALANCE and isSenior:
        genderCount = floor.numOfGender(isSenior=True)[gender]

        if ((floorSeniorCapacity - genderCount)/floorSeniorCapacity) > (0.5 + GENDER_BALANCE_PERCENTAGE_LENIENCY):
            return avaliableRooms

    if EQUALISE_ONFLOOR_GENDER_BALANCE:
        genderCount = floor.numOfGender()[gender]
        
        if (genderCount/numOfRooms) > (0.5 + GENDER_BALANCE_PERCENTAGE_LENIENCY):
            return avaliableRooms


    for room in floor.rooms:
        if not room.assigned:
            if room.front and room.balc:
                divInfo = getDivisionInformation(floorNum, room.SubDivisionNumber)

                if NUMBER_OF_SENIORS_FRONT_BALC <= divInfo["numSenior"] and isSenior:
                    continue
                
                if EQUALISE_ONBALC_GENDER_BALANCE:
                    currGenderCount = 0
                    if gender == 'm':
                        currGenderCount = divInfo["numMale"]
                    elif gender == 'f':
                        currGenderCount = divInfo["numFemale"]

                    if (divInfo["numOfRooms"] - currGenderCount)/divInfo["numOfRooms"] <= 0.5:
                        continue
                
                avaliableRooms.append(room)
                


            else:
                avaliableRooms.append(room)
    
    return avaliableRooms
                
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
    numAvaliable = 0
    numMale = 0
    numFemale = 0
    numSenior = 0
    numFresh = 0

    for room in floor.rooms:
        if room.SubDivisionNumber == division:
            divisionRooms.append(room)

            if room.assigned == False:
                numAvaliable += 1
            if room.occupant.gender == 'm':
                numMale += 1
            if room.occupant.gender == 'f':
                numFemale += 1
            if room.occupant.year > 1:
                numSenior += 1
            if room.occupant.year == 1:
                numFresh += 1

    numOfRooms = len(divisionRooms)

    return {"numOfRooms":numOfRooms, "numAvaliable":numAvaliable, "numMale":numMale, "numFemale":numFemale, "numSenior":numSenior, "numFresh":numFresh}


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
    updateAllocationCSV()
    return True

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

    for st in studentList:
        print(st.name,"-",st.assigned)