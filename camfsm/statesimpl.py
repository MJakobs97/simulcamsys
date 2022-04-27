from state import State
from ble_outsourcing import connect_ble, rec_start, rec_stop, get_or_create_eventloop, query, subscribe_status
from response import Response

import os
import sys
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
       #print("Conn_flag: ", conn_flag)
       
       
       if ((event == 'dms1') & (conn_flag == "1")):
        try:
         addresses = ""
         for client in clients:
          address = COMMAND_REQ_UUID
          
          #----COROUTINE GETS CALLED----
          global global_loop
          start_loop = global_loop
          asyncio.set_event_loop(start_loop)          
          asyncio.get_event_loop().run_until_complete(rec_start(client, address))
                  
         return RecordingState()
        except Exception as ex: 
         #print("Exception in IdleSate.on_event(): \n", ex)
         sys.exit("Rec_start failed, awaiting restart")

       if event == 'dms2':
        #print("dms2 == 1, acting accordingly")
        return ConnectingState()

       return self



class RecordingState(State):

    def __init__(self):
     print("Switched to: ", str(self))

    def on_event(self, event):
       if event == 'dms0':
        for client in clients:
         address = COMMAND_REQ_UUID
         
         #----COROUTINE GETS CALLED----
         global global_loop
         stop_loop = global_loop
         asyncio.set_event_loop(stop_loop)          
         asyncio.get_event_loop().run_until_complete(rec_stop(client, address))

        return IdleState()
       if event == 'dms1':
        #print(self.count)
        self.count+=1

        return self
    

class ConnectingState(State):
      def __init__(self):
       print("Switched to: ", str(self))

      

      def on_event(self, event):
       if event == 'dms2':
        #print("Received event: dms2 !")
        def dummy_notification_handler(handle: int, data: bytes) -> None:
         print("dummy_notification_handler running")
         #possibly move response outside of handler
         response = Response()
         response.accumulate(data)

         query_event = asyncio.Event()

         if response.is_received:
           response.parse()
           print("Response: ", response)
           
           global current_client

           #If event uuid is query_rsp_uuid append response.data to global data storage
           if current_client.services.characteristics[handle].uuid == QUERY_RSP_UUID:
            #global rsp_data
            #rsp_data.append(response.data)
            print("Response data: "+str(response))


           else:
            print("Dummy_notification_handler: received rsp != query_rsp")
           query_event.set()
           event.set()

        def periodic_query_call(clients):
          global global_loop
          periodic_loop = global_loop
          asyncio.set_event_loop(periodic_loop)

          print(rsp_data)

          #call query coroutine after 5s, do something with the data, call periodic_query_call() again
          for y in clients:
            global current_client
            current_client = y
            asyncio.get_event_loop().call_later(5, query(y, QUERY_REQ_UUID))
                              
          periodic_query_call(clients)
          

           


         
        global clients
        
        global conn_flag

        global rsp_data
        rsp_data = []

        global current_client
        current_client = BleakClient()

        global COMMAND_REQ_UUID      
        global COMMAND_RSP_UUID 
        global SETTINGS_REQ_UUID 
        global SETTINGS_RSP_UUID 
        global QUERY_REQ_UUID
        global QUERY_RSP_UUID

        global GOPRO_BASE_UUID 
        global GOPRO_BASE_URL 

        GOPRO_BASE_UUID = "b5f9{}-aa8d-11e3-9046-0002a5d5c51b"
        GOPRO_BASE_URL = "http://10.5.5.9:8080"

        COMMAND_REQ_UUID = GOPRO_BASE_UUID.format("0072")
        COMMAND_RSP_UUID = GOPRO_BASE_UUID.format("0073")
        SETTINGS_REQ_UUID = GOPRO_BASE_UUID.format("0074")
        SETTINGS_RSP_UUID = GOPRO_BASE_UUID.format("0075")
        QUERY_REQ_UUID = GOPRO_BASE_UUID.format("0076")	
        QUERY_RSP_UUID = GOPRO_BASE_UUID.format("0077")

        parser = argparse.ArgumentParser(description="Connect to a GoPro camera, pair, then enable notifications.")
        parser.add_argument("-i","--identifier",type=str,help="Last 4 digits of GoPro serial number, which is the last 4 digits of the default camera SSID. If not used, first discovered GoPro will be connected to",default=None)    
        args = parser.parse_args()


        print("Running connect_ble asynchronously...")
        try:
         #clients = asyncio.run(connect_ble(dummy_notification_handler, args.identifier))
         #clients = await connect_ble(dummy_notification_handler, args.identifier)
         global global_loop
         global_loop = asyncio.new_event_loop()
         asyncio.set_event_loop(global_loop)
         clients = asyncio.get_event_loop().run_until_complete(connect_ble(dummy_notification_handler, args.identifier))
         #periodic_query_call(clients)
         
         #now loop over clients, sending query_req gatt_char
         address = QUERY_REQ_UUID
         for s in clients:
          asyncio.get_event_loop().run_until_complete(subscribe_status(s,address))



        except Exception as ex:
         #print(ex)
         #print("-----------------------------------------------------------------------------------------------")
         #traceback.print_exc()
         sys.exit("Connection failed, must restart program! Wait ...")    


        conn_flag = "1"
        return IdleState()	
