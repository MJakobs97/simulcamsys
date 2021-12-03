from state import State
import subprocess
import re
import asyncio
import logging
import argparse
#import time
from typing import Dict, Any, List, Callable, Pattern

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice as BleakDevice

conn_flag = "0"
clients : List[BleakClient] = []

class IdleState(State):

   def __init__(self):
    print("Switched to: ", str(self))

   def on_event(self, event):
       print(event)
       global conn_flag
       print(conn_flag)
       #WARNING, THIS CONDITION IS MET, EVEN IF event == 'dms2' !
       if ((event == 'dms1') & (conn_flag == "1")):
        for client in clients:
         asyncio.run(client.write_gatt_char(COMMAND_REQ_UUID, bytearray([3, 1, 1, 1])))
        return RecordingState()
       
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
         asyncio.run(client.write_gatt_char(COMMAND_REQ_UUID, bytearray([3, 1, 1, 0])))
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
    
        print("Running connect_ble asynchronously...")
        #clients = await connect_ble(dummy_notification_handler, identifier)
        clients = asyncio.run(connect_ble(dummy_notification_handler, identifier))
        conn_flag = "1"
        return IdleState()	


