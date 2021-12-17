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
          loop = get_or_create_eventloop()
          future = asyncio.run_coroutine_threadsafe((rec_start(client, address)), loop)
          result = future.result()
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
         loop = get_or_create_eventloop() 
         future = asyncio.run_coroutine_threadsafe((rec_stop(client, address)), loop)
         result = future.result()

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


        print("Running connect_ble asynchronously...")

        try:
         clients = asyncio.run(connect_ble(dummy_notification_handler, args.identifier),  debug=True)
        except Exception as ex: 
         print("Error while connecting: ", ex)
         traceback.print_exc()



        conn_flag = "1"
        return IdleState()	