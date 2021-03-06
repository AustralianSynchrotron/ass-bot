#!/usr/bin/env python
#

# Collect system variables and send to display and other ports


__author__ = 'Cameron Rodda'
__version__ = '0.0.1'
__date__ = '21 August 2013'

import commands
import zmq
import time
from ctypes import *
import sys
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, CurrentChangeEventArgs, InputChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.MotorControl import MotorControl

#Create a motor control object
try:
    mcL = MotorControl() # Left Motor
    mcR = MotorControl() # Right Motor
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)

try:
    #mcL.openPhidget(serial=298857)
    #mcR.openPhidget(serial=298856)
    mcL.openRemote('odroid',serial=298857)
    mcR.openRemote('odroid',serial=298856)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

try:
    mcL.waitForAttach(10000)
    mcR.waitForAttach(10000)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    try:
        mcL.closePhidget()
        mcR.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    print("Exiting....")
    exit(1)

print("mcL attached to WebService: %s" % mcL.isAttachedToServer())
print("mcR attached to WebService: %s" % mcR.isAttachedToServer())

context = zmq.Context()
bat_socket = context.socket(zmq.PUB)
bat_socket.bind("ipc:///tmp/battery.ipc")

charging = 1

while True:
    bat1 = mcL.getSupplyVoltage()
    bat2 = mcR.getSupplyVoltage()

    if ((bat1 > 26.0) or (bat2 > 26.0)):
        chargeState = 'Charging'
        bat_time = 0
        charging = 1
    else:
        chargeState = 'Discharging'
        if charging:
            # if previous state charging, then save a time stamp to calc time on battery
            start_time = int(time.time())
        charging = 0
        bat_time = (int(time.time()) - start_time) / 60.0
    
    #print("Battery1: %s, Battery2: %s" % (bat1, bat2))
    msg = {'battery1': str(bat1), 'battery2': str(bat2), 'onCharge': chargeState, 'batODO': bat_time }
    print msg
    bat_socket.send_json(msg)
    time.sleep(10.0) #battery voltage only changes relatively slowly - no need for great update rate


mcL.closePhidget()
mcR.closePhidget()

exit(1)
