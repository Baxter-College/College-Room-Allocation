from app import updateData
from models import SystemInformation
import datetime

def pauseSystem():
    sysInfo = SystemInformation.getSysInfo()
    sysInfo.systemIsRunning = False
    sysInfo.save()
    print("System Paused")
    print(f"Pause time: {datetime.datetime.now()}")

def playSystem():
    sysInfo = SystemInformation.getSysInfo()
    sysInfo.systemIsRunning = True
    sysInfo.save()
    print("System Played")
    print(f"Play time: {datetime.datetime.now()}")

def dataUpdate():
    print("Starting data update")
    updateData()
    print("Data update DONE")