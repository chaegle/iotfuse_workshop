"""
Copyright (c) 2018, Digi International, Inc.
IoT Fuse 2019 Workshop example code released under MIT License.

"""

from micropython import const
import network
import time
from machine import I2C
from hdc1080 import HDC1080
from remotemanager import RemoteManagerConnection
import xbee

send_interval = 10 # number of seconds between sensor reads/reports
i2c = I2C(1)
sensor = HDC1080(i2c, 64)
credentials = {'username': "{your_username}", 'password': "{your_password}"}
rm = RemoteManagerConnection(credentials=credentials)
hum = sensor.read_humidity()
temp = sensor.read_temperature(True)
c = network.Cellular()
   
 
def wait_for_connection():
    #print("Waiting on connection...")
    while not c.isconnected():
        print('Waiting on connection...')
        time.sleep(3)
    #print(c.ifconfig())

def post_datapoint(streamID="", data=0):
    #print("adding datapoints")
    rm.add_datapoint(streamID, data)
    
def initialize(): 
    global mydevid, lasttime
    #print("Waiting on connection...")
    lasttime = time.time()    
    # read the IMEI and creat a device ID to that matches the device ID created in Remote Manager
    device_im = xbee.atcmd("IM")
    last=device_im[-8:]
    first=device_im[:7]
    total=first+"-"+last
    mydevid="00010000-00000000-0"+total+"/"
    #print("Device ID = "+mydevid)
    hum_stream_info = {
        'description': 'Humidity',
        'id': mydevid+'Humidity',
        'type': "DOUBLE",
        'units':'%'
        }

    temp_stream_info = {
        'description': 'Temperature',
        'id': mydevid+'Temperature',
        'type': "DOUBLE",
        'units':'C'
        }
    rm.create_datastream(hum_stream_info)
    rm.create_datastream(temp_stream_info)
    
def loop():
    global lasttime
    
    while True:
        try:    
            hum = sensor.read_humidity()
            temp = sensor.read_temperature(True)
            if time.time() - lasttime > send_interval:
                lasttime = time.time()        
                post_datapoint(streamID = mydevid+"Humidity", data = hum)
                post_datapoint(streamID = mydevid+"Temperature", data = temp)
        except Exception as E:
            print(str(E))
            wait_for_connection()
    
wait_for_connection()
initialize()
loop()
