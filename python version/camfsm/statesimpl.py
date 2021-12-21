from state import State
from ble_outsourcing import connect_ble, rec_start, rec_stop, get_or_create_eventloop

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
global_loop = ""

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
          
          #----COROUTINE GETS CALLED----
          start_loop = asyncio.new_event_loop()
          asyncio.set_event_loop(start_loop)
          
          future = asyncio.get_event_loop().create_task(rec_start(client, address, start_loop))
          asyncio.get_event_loop().run_until_complete(future)
                  
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
         #----THIS ----
         #loop = asyncio.new_event_loop()
         #asyncio.set_event_loop(loop)
         #print("Is loop closed: \n", loop.is_closed())
         #print("Going to execute on this particular loop: \n", loop)         
         #future = asyncio.ensure_future(rec_stop(client, address))
         #loop.run_until_complete(future)

         #----DOES THE SAME AS THIS, YET EVERYTIME THE EXCEPTION "EVENT LOOP IS CLOSED" IS RAISED----
         #asyncio.run(rec_stop(client, address))
         #await client.write_gatt_char(address, bytearray([3, 1, 1, 0]))

         #----Testing NEW WAY TO CALL COROUTINE----
         asyncio.set_event_loop(asyncio.new_event_loop())
         #get_or_create_eventloop().run_until_complete(rec_stop(client, address, asyncio.get_event_loop()))
         asyncio.get_event_loop().run_until_complete(rec_stop(client, address, asyncio.get_event_loop()))

         #asyncio.get_event_loop().run_until_complete(rec_stop(client, address))
         #future = asyncio.ensure_future(rec_stop(client, address))   
         #asyncio.get_event_loop().run_until_complete(future)
         
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
         #clients = asyncio.run(connect_ble(dummy_notification_handler, args.identifier))
         #clients = await connect_ble(dummy_notification_handler, args.identifier)
         clients = asyncio.new_event_loop().run_until_complete(connect_ble(dummy_notification_handler, args.identifier))
        except Exception as ex:
         print(ex)
         print("-----------------------------------------------------------------------------------------------")
         traceback.print_exc()

        conn_flag = "1"
        return IdleState()	
