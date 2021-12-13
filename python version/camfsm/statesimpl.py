from state import State
from ble_outsourcing import connect_ble, rec_start, rec_stop, get_or_create_eventloop, rec_start_norm

import os
import subprocess
import re
import asyncio
import logging
import argparse
import traceback
from typing import Dict, Any, List, Callable, Pattern

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice as BleakDevice

conn_flag = "0"
clients : List[BleakClient] = []

class IdleState(State):

   def __init__(self):
    print("Switched to: ", str(self))

   def on_event(self, event):
       print("Event: ", event)
       global conn_flag
       print("Conn_flag: ", conn_flag)
       
       
       if ((event == 'dms1') & (conn_flag == "1")):
        try:
         addresses = ""
         for client in clients:
          address = COMMAND_REQ_UUID
          asyncio.run(rec_start(client, address))
          #rec_start_norm(client, address)
          #addresses = addresses + client.address + " " 
         #call = "sudo python ./main.py --address "+addresses+" --command "+ """ +"record start"+ """
         #os.system(call)
         return RecordingState()
        except Exception as ex: 
         print("Exception in IdleSate.on_event(): \n", ex)

       if event == 'dms2':
        print("dms2 == 1, acting accordingly")
        return ConnectingState()

       return self



class RecordingState(State):

    def __init__(self):
     print("Switched to: ", str(self))

    def on_event(self, event):
       if event == 'dms0':
        for client in clients:
         address = COMMAND_REQ_UUID
         asyncio.run(rec_stop(client, address))

        return IdleState()
       if event == 'dms1':
        print(self.count)
        self.count+=1

        return self
    

class ConnectingState(State):
      def __init__(self):
       print("Switched to: ", str(self))

      

      def on_event(self, event):
       if event == 'dms2':
        print("Received event: dms2 !")
        def dummy_notification_handler(handle: int, data: bytes) -> None:
         ...
        global clients
        global conn_flag


        global COMMAND_REQ_UUID      
        global COMMAND_RSP_UUID 
        global SETTINGS_REQ_UUID 
        global SETTINGS_RSP_UUID 

        global GOPRO_BASE_UUID 
        global GOPRO_BASE_URL 

        GOPRO_BASE_UUID = "b5f9{}-aa8d-11e3-9046-0002a5d5c51b"
        GOPRO_BASE_URL = "http://10.5.5.9:8080"

        COMMAND_REQ_UUID = GOPRO_BASE_UUID.format("0072")
        COMMAND_RSP_UUID = GOPRO_BASE_UUID.format("0073")
        SETTINGS_REQ_UUID = GOPRO_BASE_UUID.format("0074")
        SETTINGS_RSP_UUID = GOPRO_BASE_UUID.format("0075")	
	
        parser = argparse.ArgumentParser(description="Connect to a GoPro camera, pair, then enable notifications.")
        parser.add_argument("-i","--identifier",type=str,help="Last 4 digits of GoPro serial number, which is the last 4 digits of the default camera SSID. If not used, first discovered GoPro will be connected to",default=None)    
        args = parser.parse_args()


        #try:
         #print("Data about event loop b4 connect_ble: \n")
         #loop = asyncio.get_event_loop()
         #print("Loop: \n", loop)
         #print("\n\n")
        #except:
         #print("No running loop!")
         #print("\n\n")     


        print("Running connect_ble asynchronously...")
        #clients = await connect_ble(dummy_notification_handler, identifier)
        try:
         print("Current Loop: \n", asyncio.get_running_loop())
        except Exception as ex:
         print("Exception before asyncio.run(): \n", ex)
        try:
         clients = asyncio.run(connect_ble(dummy_notification_handler, args.identifier))
        except Exception as ex:
         print(ex)
         print("-----------------------------------------------------------------------------------------------")
         traceback.print_exc()


        #try:
         #print("Data about event loop after connect_ble: \n")
         #loop = asyncio.get_event_loop()
         #print("Loop: \n", loop)
         #print("\n\n")
        #except:
         #print("No running loop!")
         #print("\n\n")   

        conn_flag = "1"
        return IdleState()	
