from flask import Flask, render_template, request, json
from allocation import listAvaliableRooms, makeAllocation
from people import getStudentList
import json

app = Flask(__name__)

#TODO: everything that needs to be done on startup

@app.before_request
def before_request():
    #TODO: everythin that needs to be done before a request
    pass

@app.route("/rooms/select", methods=["GET"])
def select_rooms():
    #TODO: get the data from fucntions
    data = get_data()

    return render_template("select.html", data=data)

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
    app.run()