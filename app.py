#!/usr/bin/env python3
from flask import Flask, render_template, request, json
from allocation import listAvailableRooms, makeAllocation, createFloors, loadAllocatedCSV
from people import getStudentList, checkCorrectPassword, checkValidTime
from rooms import roomOccupied
import datetime
import json

app = Flask(__name__)

createFloors()
loadAllocatedCSV()

@app.before_request
def before_request():
    #TODO: everythin that needs to be done before a request
    # re-load from db/csv
    # fill freshers
    pass

@app.route("/", methods=["GET","POST"])
def select_rooms():
    
    if request.method == "GET":
        data = get_data()
        return render_template("select.html", data=data)

    elif request.method == "POST":
        form = request.form
        if (form["submit"] == "secure my room"):
            zid = form["zid"]
            password = form["code"]
            firstPref = form["first_room"]
            subPref = [form["pref1"], form["pref2"], form["pref3"], form["pref4"], form["pref5"]]
            checker = checkValidRoomRequest(zid, password, firstPref, subPref)
            return render_template("submitted.html", data=checker)
    else:
        # TODO: major error handler
        pass

    

def checkValidRoomRequest(zid, password, firstPreference, subPreferences):
    errors = []
    time = datetime.datetime.now()
    if(not checkCorrectPassword(zid, password)):
        errors.append("incorrect password")
    # TODO: TIME CHECKS
    # if (not checkValidTime(zid, time)):
    #     errors.append("before valid submit time")
    
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
        maleList[str(floorNum)] = listAvailableRooms(floorNum, "m", True)
        femaleList[str(floorNum)] = listAvailableRooms(floorNum, "f", True)
    
    allData = {"ZIDS":studentList, "MALE":maleList, "FEMALE":femaleList}

    return allData

if __name__ == "__main__":
    app.run(debug=True, port=8888)