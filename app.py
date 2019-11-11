from flask import Flask, render_template, request, json
from allocation import listAvaliableRooms, makeAllocation
from people import getStudentList, checkCorrectPassword
from rooms import roomOccupied
import datetime
import json

app = Flask(__name__)

#TODO: everything that needs to be done on startup

@app.before_request
def before_request():
    #TODO: everythin that needs to be done before a request
    # re-load from db/csv
    # fill freshers
    pass

@app.route("/rooms/select", methods=["GET","POST"])
def select_rooms():
    
    if request.method == "GET":
        data = get_data()

        return render_template("select.html", data=data)

    elif request.method == "POST":
        form = request.form
        if (form["submit"] == "SUBMIT"):
            # DEBUG: update this: room as identifier is wrong
            zid = 
            password = 
            firstPref = 
            subPref = 
            checker = checkValidRoomRequest(form)
            return redirect(url_for('home'))
    else:
        # TODO: major error handler
        pass

    

def checkValidRoomRequest(zid, password, firstPreference):
    errors = []
    time = datetime.datetime.now()
    if(not checkCorrectPassword(zid, password)):
        errors.append("incorrect password")
    # TODO: check valid time
    
    validRoom = roomOccupied(firstPreference)
    if(validRoom["occupied"]):
        if (validRoom["found"]):
            errors.append("room is occupied")
        else:
            errors.append("room not found or invalid room number")
    
    return {"valid":(len(errors) == 0), "errors":errors}
    
    

def get_data():
    studentList = getStudentList()
    maleList = {}
    femaleList = {}

    for floorNum in range(1,8):
        maleList[floorNum] = listAvaliableRooms(floorNum, "m", True)
        femaleList[floorNum] = listAvaliableRooms(floorNum, "f", True)
    
    allData = {"ZIDS":studentList, "MALE":maleList, "FEMALE":femaleList}

    return json.dumps(allData)

if __name__ == "__main__":
    app.run(debug=True, port=8888)