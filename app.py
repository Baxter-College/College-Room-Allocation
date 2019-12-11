#!/usr/bin/env python3
from flask import Flask, render_template, request, json, jsonify, redirect, url_for
from io import StringIO
from allocation import listAvailableRooms, makeAllocation
from people import (
    getStudentList,
    checkCorrectPassword,
    checkValidTime,
    checkPersonAllocated,
    createAccessTimes
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
from models import db_reset
import csv
import os

db_reset()
# createAccessTimes("10:30AM 12/11/2019")

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
            if checker["valid"]:
                makeAllocation(zid, int(firstPref), subPref)
            return render_template("submitted.html", data=checker)
    else:
        # TODO: major error handler
        pass


@app.route("/upload/file", methods=["GET", "POST"])
def upload():
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
            return redirect("/")


@app.route("/upload/people", methods=["POST"])
def upload_p():
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
            return redirect("/")


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
        roomList = listAvailableRooms(
            (math.floor(roomNum / 100)), getStudentList()[zid], True
        )
        print(roomNum, roomList)
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

