'''
    Rules in order of importance:
        - Tries to keep the total number of second yeas on each floor equal
        - Must try to keep the number of males and females on each floor even
        - For every front balc, there must be at least 2 freshers
        - Must try to keep the number of first years / second years on each floor even
        - Tries to keep the number of bad rooms remaining for freshers to a minimum
        
'''

from people import studentList, Student, findPerson, NUM_OF_SENIORS, NUM_OF_FRESHERS
from rooms import roomList, Room, findRoom
import math
floorList = []

class Floor():
    def __init__(self, floorNumber, rooms):
        self.floorNumber = floorNumber
        self.rooms = rooms

    # Includes limitations with front balcs
    def listAvaliableRooms(self, gender=None, isSenior = False):
        avaliableRooms = []

        for room in self.rooms:
            if room.assigned == False:
                if gender == None:
                    avaliableRooms.append(room)
                else:
                    # {'numOccupied':numOccupied, 'numMale':numMale, 'numFemale':numFemale, 'numSenior':numSenior}
                    if room.front == True and room.balc == True:
                        frontBalc = self.frontBalconyAllowance(room)
                        if isSenior == True:
                            if frontBalc["numSenior"] < 2:
                                if gender == 'm' and frontBalc["numMale"] < 2:
                                    avaliableRooms.append(room)
                                elif gender == 'f' and frontBalc["numFemale"] < 2:
                                    avaliableRooms.append(room)
                                else:
                                    avaliableRooms.append(room)
                        # NOTE: This means you can have more than 2 freshers on a balc (unlikely though)
                        else:
                            if gender == 'm' and frontBalc["numMale"] < 2:
                                avaliableRooms.append(room)
                            elif gender == 'f' and frontBalc["numFemale"] < 2:
                                avaliableRooms.append(room)
                            else:
                                avaliableRooms.append(room)
                    else:
                        avaliableRooms.append(room)
                        

                    
        return avaliableRooms

    @property
    def allocationPercentage(self):
        numRooms = len(self.rooms)
        numOccupied = 0

        for room in self.rooms:
            if room.assigned == True:
                numOccupied += 1
        
        return ((numOccupied/numRooms)*100)

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

    @property
    def seniorFresherRatio(self):
        seniorCount = self.numOfSeniors
        fresherCount = self.numOfFreshers
        
        if seniorCount == 0 or fresherCount == 0:
            return 0
        else:
            return seniorCount/fresherCount

    def numOfMale(self, isSenior):
        maleCount = 0

        for room in self.rooms:
            if room.assigned == True:
                if room.occupant.gender == "m":
                    if isSenior == True and room.occupant.year > 1:
                        maleCount += 1
                    elif isSenior == False:
                        maleCount += 1
        
        return maleCount

    def numOfFemale(self, isSenior):
        femaleCount = 0

        for room in self.rooms:
            if room.assigned == True:
                if room.occupant.gender == "f":
                    if isSenior == True and room.occupant.year > 1:
                        femaleCount += 1
                    elif isSenior == False:
                        femaleCount += 1
        
        return femaleCount
    
    # NOTE: only takes male and female, other doesn't effect ratio
    @property
    def genderRatio(self):
        maleCount = self.numOfMale(False)
        femaleCount = self.numOfFemale(False)
        
        
        if maleCount == 0 or femaleCount == 0:
            return 0
        else:
            return maleCount/femaleCount

    # the number of seniors that can fit in on the floor evenly
    @property
    def seniorCapacity(self):
        overflow = NUM_OF_SENIORS % 7
        if overflow != 0:
            if (overflow + self.floorNumber) > 7:
                maxNumOfSeniors = math.floor(NUM_OF_SENIORS/7)+1
            else:
                maxNumOfSeniors = math.floor(NUM_OF_SENIORS/7)
        else:
            maxNumOfSeniors = NUM_OF_SENIORS/7
        
        # self.numOfSeniors-maxNumOfSeniors
        return maxNumOfSeniors

    # The remaining number of senior male/female spots on a floor
    @property
    def seniorGenderCapacity(self):
        # This indicates what percentage of second year gender ratio to allow, set to 0.5 for second year has to be even, 1 for doesn't matter
        CUTOFF_GENDER_RATIO = 0.75

        maleCount = self.numOfMale(True)
        femaleCount = self.numOfFemale(True)

        maleRemaining = math.floor(self.seniorCapacity * CUTOFF_GENDER_RATIO) - maleCount
        femaleRemaining = math.floor(self.seniorCapacity * CUTOFF_GENDER_RATIO) - femaleCount

        return {"m":maleRemaining,"f":femaleRemaining}
        

    def frontBalconyAllowance(self, room):
        if type(room) == str or type(room) == int:
            room = findRoom(roomList, int(room))
        
        balcList = []

        numOccupied = 0
        numMale = 0
        numFemale = 0
        numSenior = 0

        for sharedBalcRoom in self.rooms:
            if room.balcNumber == sharedBalcRoom.balcNumber and sharedBalcRoom.assigned == True:
                balcList.append(sharedBalcRoom)

                if sharedBalcRoom.assigned == True:
                    numOccupied += 1
                
                if sharedBalcRoom.occupant.gender == 'm':
                    numMale += 1
        
                if sharedBalcRoom.occupant.gender == 'f':
                    numFemale += 1
                
                if sharedBalcRoom.occupant.year > 1:
                    numSenior += 1
        
        return {'roomList':balcList, 'numOccupied':numOccupied, 'numMale':numMale, 'numFemale':numFemale, 'numSenior':numSenior}


    def listValidRooms(self, year, gender):
        avaliableRooms = []
        if year > 1:
            # If there are more than the allowable number of seniors on a floor
            if self.numOfSeniors-self.seniorCapacity == 0:
                return avaliableRooms
            
            # if the genders of the seniors is greater than the weighted capacity
            genderCapacity = self.seniorGenderCapacity
            if gender == 'm' or gender == 'f':
                if genderCapacity[gender] == 0:
                    return avaliableRooms

            return self.listAvaliableRooms(gender=gender,isSenior=True)
        
        else:
            if gender == 'm':
                if self.numOfMale - self.numOfFemale > 2:
                    return avaliableRooms
                else:
                    return self.listAvaliableRooms(gender=gender,isSenior=False)
            elif gender == 'f':
                if self.numOfFemale - self.numOfMale > 2:
                    return avaliableRooms
                else:
                    return self.listAvaliableRooms(gender=gender,isSenior=False)
            else:
                    return self.listAvaliableRooms(gender=gender,isSenior=False)
            
        
def allAvaliableRooms(year, gender):
    avaliableRooms = []
    for floorNum in range(7):
        avaliableRooms.extend(floorList[floorNum].listValidRooms(year,gender))
    
    return avaliableRooms

# Will return True if succsess, False if fail
def makeAllocation(person, newRoom):
    student = findPerson(studentList, person)
    if type(newRoom) == str or type(newRoom) == int:
        newRoom = findRoom(roomList, int(newRoom))

    if student == False or newRoom == False:
        return False

    if newRoom.assigned == True:
        return False
    
    if student.assigned == True:
        oldRoom = student.allocation
        oldRoom.clearAllocation()
    
    newRoom.assignRoom(student)
    student.assignRoom(newRoom)
    return True

def createFloors():
    for floorNum in range(1,8):
        newList = []
        for room in roomList:
            if room.floor == floorNum:
                newList.append(room)
        
        newFloor = Floor(floorNum, newList)
        floorList.append(newFloor)


if __name__ == "__main__":
    createFloors()
    allAvaliableRooms(2, 'm')