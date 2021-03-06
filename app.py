#!/usr/bin/env python3
from flask import Flask, render_template, request, json, jsonify, redirect, url_for, make_response, after_this_request
from io import StringIO
from allocation import listAvailableRooms, makeAllocation, allocationsToCSV
from people import (
    getStudentList,
    checkCorrectPassword,
    checkValidTime,
    checkPersonAllocated,
    createAccessTimes,
    checkValidRoomType,
    personAllocatedList,
    model_to_dict,
    sendEmails
)
from people import (
    getStudentsByRoomPoints,
    calculatePercentageAllocated,
    import_students,
    studentExists
)
from rooms import roomOccupied, import_rooms, basicImportRoom
import datetime
import json
import math
from models import db_reset, SystemInformation, dbWipe
import csv
import os


if "HEROKU" in os.environ:
    ADMIN_PAGE_PASSWORD = os.environ["ADMIN_PAGE_PASSWORD"]
    WIPE_DB_PASSWORD = os.environ["WIPE_DB_PASSWORD"]
else:
    ADMIN_PAGE_PASSWORD = "BAXTERROOMS2019!"
    WIPE_DB_PASSWORD = "IUYb_ouiYOU_ypV07!bU"

allData = ''

db_reset()
if (not SystemInformation.getSysInfo().roomListUploaded):
    basicImportRoom()
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def select_rooms():

    if request.method == "GET":
        # start = datetime.datetime.now()
        global allData
        data = allData
        # print("--------------------TIMEDIFF:",datetime.datetime.now().microsecond - start.microsecond,"--------------------")
        return render_template("select.html", data=data)

    elif request.method == "POST":
        form = request.form
        if form["submit"] == "Submit my Preferences":
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
            extraInformation = form["submissionNotes"]
            checker = checkValidRoomRequest(zid, password, firstPref, subPref)
            if checker["valid"]:
                makeAllocation(zid, int(firstPref), subPref, extraInformation)
                return redirect(url_for("submissionAccepted"))
            return render_template("submitted.html", data=checker)
        else:
            return "UNKNOWN ERROR, message Tom Wright please!"
    else:
        return "UNKNOWN ERROR, message Tom Wright please!"

@app.route("/submitted", methods=["GET"])
def submissionAccepted():
    checker = {"valid": True, "errors": []}
    
    @after_this_request
    def refreshData(response):
        updateData()
        return response

    return render_template("submitted.html", data=checker)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    password = request.args.get('p')
    if (password != ADMIN_PAGE_PASSWORD):
        return "ACCESS DENIED"

    if request.method == "POST":
        form = request.form
        if (form["submit"] == "Begin Time Setting" or form["submit"] == "Re-Set Times" ):
            date = form['starttime']
            seperation = form['timeSeperation']
            createAccessTimes(str(date), int(seperation))
            @after_this_request
            def refreshData(response):
                updateData()
                return response
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

@app.route("/admin/upload/rooms", methods=["POST"])
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

            @after_this_request
            def refreshData(response):
                updateData()
                return response
            return "SUCCESSFULLY UPLOADED ROOMS"

@app.route("/admin/upload/people", methods=["POST"])
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

            @after_this_request
            def refreshData(response):
                updateData()
                return response
            return "SUCCESSFULLY UPLOADED PEOPLE"

@app.route("/admin/allocated", methods=["GET"])
def allocated():
    return jsonify({"allocated": calculatePercentageAllocated()})

@app.route("/admin/sendMail", methods=["GET"])
def sendMail():
    sendEmails(app) # send password / times emails

    sysInfo = SystemInformation.getSysInfo()
    sysInfo.mailOutDone = True
    sysInfo.save()

    return "MAILOUT SUCCESSFUL"

@app.route("/admin/wipe/db", methods=["GET"])
def wipeDB():
    password = request.args.get('p')
    if (password == WIPE_DB_PASSWORD):
        dbWipe()

    @after_this_request
    def refreshData(response):
        basicImportRoom()
        updateData()
        return response
    return "DATABASE WIPED"

@app.route("/admin/PAUSE_THAT_ALLOCATION_SYSTEM", methods=["GET"])
def allocationPause():
    
    sysInfo = SystemInformation.getSysInfo()
    sysInfo.systemIsRunning = False
    sysInfo.save()
    
    return "ALLOCATION SYSTEM PAUSED"

def checkValidRoomRequest(zid, password, firstPreference, subPreferences):
    errors = []
    
    if (not SystemInformation.getSysInfo().systemIsRunning):
        return {"valid": False, "errors": ["The Allocation system is paused, this is probably because of an error in the system that we are trying to fix. No one is currently able to choose their rooms. We will post on the Baxter 2019 Facebook page shortly."]}

    if (not studentExists(zid)):
        return {"valid": False, "errors": ["zID is incorrect. Message Tom, Tom or Rohan or try again"]}

    if (SystemInformation.studentListUploaded and SystemInformation.roomListUploaded):
        personAllocation = checkPersonAllocated(zid)
        if personAllocation["allocated"]:
            errors.append(
                f"You are already allocated to room '{personAllocation['room']}'."
            )

        if not checkCorrectPassword(zid, password):
            errors.append("incorrect password")
        if not checkValidTime(zid):
            errors.append("You tried to submit before your submit time")

        validRoom = roomOccupied(firstPreference)
        if validRoom["occupied"]:
            if validRoom["found"]:
                errors.append("Room is occupied")
            else:
                errors.append("Room number not found or invalid room number")
        else:
            roomNum = int(firstPreference)
            roomList = listAvailableRooms(
                (math.floor(roomNum / 100)), getStudentList()[zid]['gender'], True
            )
            if not roomList[firstPreference]["available"]:
                errors.append("Cannot allocate room due to rule")

            if not checkValidRoomType(zid, roomNum):
                errors.append("Cannot allocate due to your room preferences (Ensuite/Standard Room)")
    else:
            errors.append("ERROR: Data not loaded")

    return {"valid": (len(errors) == 0), "errors": errors}

def updateData():
    studentList = getStudentList()
    maleList = {}
    femaleList = {}

    for floorNum in range(1, 8):
        maleList[str(floorNum)] = listAvailableRooms(floorNum, "m", True)
        femaleList[str(floorNum)] = listAvailableRooms(floorNum, "f", True)

    global allData
    allData = {"ZIDS": studentList, "MALE": maleList, "FEMALE": femaleList}

updateData()


if __name__ == "__main__":
    # send_message()
    if "HEROKU" in os.environ:
        PORT = int(os.environ.get("PORT"))
        app.run(host="0.0.0.0", port=PORT)
    else:
        PORT = 8888
        app.run(debug=True, host="0.0.0.0", port=PORT)