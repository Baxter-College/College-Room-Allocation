#!/usr/bin/env python3
from flask import Flask, render_template, request, json, jsonify, redirect, url_for, make_response
from io import StringIO
from allocation import listAvailableRooms, makeAllocation, allocationsToCSV
from people import (
    getStudentList,
    checkCorrectPassword,
    checkValidTime,
    checkPersonAllocated,
    createAccessTimes,
    personAllocatedList,
    model_to_dict
)
from people import (
    getStudentsByRoomPoints,
    calculatePercentageAllocated,
    import_students,
)
from rooms import roomOccupied, import_rooms
from mail import send_message
import datetime
import pytz
import json
import math
from models import db_reset, SystemInformation, dbWipe
import csv
import os

ADMIN_PAGE_PASSWORD = "BAXTERROOMS2019!"
WIPE_DB_PASSWORD = "IUYb_ouiYOU_ypV07!bU"

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
        # start = datetime.datetime.now()
        data = get_data()
        # print("--------------------TIMEDIFF:",datetime.datetime.now().microsecond - start.microsecond,"--------------------")
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
            if checker["valid"]:
                makeAllocation(zid, int(firstPref), subPref)
            return render_template("submitted.html", data=checker)
    else:
        # TODO: major error handler
        pass

@app.route("/upload/rooms", methods=["POST"])
def upload_rooms():
    if request.method == "GET":
        return render_template("upload.html")
    else:
        if "file" not in request.files:
            print("no file")
            return redirect(url_for("/upload/file"))
        else:
            file = request.files["file"]
            # file = open("smth")
            string = file.read().decode("utf-8")  #

            # file = TextIOWrapper(file, encoding='utf-8')
            if file.filename == "":
                return redirect(request.url)
            csv_file = csv.DictReader(StringIO(string))
            import_rooms(csv_file)
            return "SUCCESSFULLY UPLOADED ROOMS"

@app.route("/upload/people", methods=["POST"])
def upload_people():
    if request.method == "GET":
        return render_template("upload.html")
    else:
        if "file" not in request.files:
            print("no file")
            return redirect(url_for("/upload/file"))
        else:
            file = request.files["file"]
            # file = open("smth")
            string = file.read().decode("utf-8")  #

            # file = TextIOWrapper(file, encoding='utf-8')
            if file.filename == "":
                return redirect(request.url)
            csv_file = csv.DictReader(StringIO(string))
            import_students(csv_file)
            return "SUCCESSFULLY UPLOADED PEOPLE"


@app.route("/admin", methods=["GET", "POST"])
def admin():
    password = request.args.get('p')
    if (password != ADMIN_PAGE_PASSWORD):
        return "ACCESS DENIED"

    if request.method == "POST":
        form = request.form
        if (form["submit"] == "Begin Room Allocation" or form["submit"] == "Restart Room Allocation" ):
            date = form['starttime']
            createAccessTimes(str(date))
        elif (form["submit"] == "Download File"):
            si = StringIO()
            cw = csv.writer(si)
            cw.writerows(allocationsToCSV())
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = "attachment; filename=roomAllocations.csv"
            output.headers["Content-type"] = "text/csv"
            return output


    return (render_template("admin.html", 
                            students=getStudentsByRoomPoints(), 
                            allocations=personAllocatedList(), 
                            info=model_to_dict(SystemInformation.getSysInfo()),
                            dbWipePass=WIPE_DB_PASSWORD))


@app.route("/admin/allocated", methods=["GET"])
def allocated():
    return jsonify({"allocated": calculatePercentageAllocated()})

@app.route("/admin/wipe/db", methods=["GET"])
def wipeDB():
    password = request.args.get('p')
    if (password == WIPE_DB_PASSWORD):
        dbWipe()
    return "DATABASE WIPED"

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
        roomList = listAvailableRooms(
            (math.floor(roomNum / 100)), getStudentList()[zid], True
        )
        if not roomList[firstPreference]["available"]:
            errors.append("cannot allocate room due to rule")

    return {"valid": (len(errors) == 0), "errors": errors}


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
    if "HEROKU" in os.environ:
        PORT = int(os.environ.get("PORT"))
        app.run(host="0.0.0.0", port=PORT)
    else:
        PORT = 8888
        app.run(debug=True, host="0.0.0.0", port=PORT)