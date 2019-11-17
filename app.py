#!/usr/bin/env python3
from flask import Flask, render_template, request, json, jsonify
from allocation import listAvailableRooms
from people import getStudentList, checkCorrectPassword, checkValidTime, checkPersonAllocated
from rooms import roomOccupied, makeAllocation
from rooms import roomOccupied
from mail import send_message
import datetime
import pytz
import json
import math
from dotenv import load_dotenv #pylint: disable=unused-wildcard-import
from models import db_reset

db_reset()

app = Flask(__name__)



@app.before_request
def before_request():
    # TODO: everythin that needs to be done before a request
    # re-load from db/csv
    # fill freshers
    pass


@app.route("/", methods=["GET", "POST"])
def select_rooms():

    if request.method == "GET":
        data = get_data()
        return render_template("select.html", data=data)

    elif request.method == "POST":
        form = request.form
        if form["submit"] == "secure my room":
            zid = form["zid"]
            password = form["code"]
            firstPref = form["first_room"]
            subPref = [
                form["pref1"],
                form["pref2"],
                form["pref3"],
                form["pref4"],
                form["pref5"],
            ]
            checker = checkValidRoomRequest(zid, password, firstPref, subPref)
            if (checker["valid"]):
                makeAllocation(zid, int(firstPref), subPref)
            return render_template("submitted.html", data=checker)
    else:
        # TODO: major error handler
        pass


@app.route("/mailer", methods=["GET", "POST"])
def mailer():
    if request.method == "GET":
        return render_template("mailer.html", students=getStudentsByRoomPoints())


@app.route("/allocated", methods=["GET"])
def allocated():
    return jsonify({"allocated": calculatePercentageAllocated()})


def checkValidRoomRequest(zid, password, firstPreference, subPreferences):
    errors = []
    time = datetime.datetime.now()
    pytz.timezone("Australia/Sydney").localize(time)

    personAllocation = checkPersonAllocated(zid)
    if personAllocation["allocated"]:
        errors.append(
            f"You are already allocated to room '{personAllocation['room']}'."
        )

    if not checkCorrectPassword(zid, password):
        errors.append("incorrect password")
    # TODO: TIME CHECKS
    if not checkValidTime(zid, time):
        errors.append("before valid submit time")

    validRoom = roomOccupied(firstPreference)
    if validRoom["occupied"]:
        if validRoom["found"]:
            errors.append("room is occupied")
        else:
            errors.append("room not found or invalid room number")
    else:
        roomNum = int(firstPreference)
        roomList = listAvailableRooms((math.floor(roomNum/100)), getStudentList()[zid], True)
        print(roomNum,roomList)
        if (not roomList[firstPreference]['available']):
            errors.append("cannot allocate room due to rule")
    
    return {"valid":(len(errors) == 0), "errors":errors}
    
    

def get_data():
    studentList = getStudentList()
    maleList = {}
    femaleList = {}

    for floorNum in range(1, 8):
        maleList[str(floorNum)] = listAvailableRooms(floorNum, "m", True)
        femaleList[str(floorNum)] = listAvailableRooms(floorNum, "f", True)

    allData = {"ZIDS": studentList, "MALE": maleList, "FEMALE": femaleList}

    return allData


if __name__ == "__main__":
    # send_message()
    app.run(debug=True, port=8888)

