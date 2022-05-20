from state import State
from ble_outsourcing import connect_ble, rec_start, rec_stop, get_or_create_eventloop, subscribe_status, await_responses, get_status
from notification_outsourcing import compare_and_remove, upload_data, run_async_another_thread
from response import Response


import os
import sys
import subprocess
import threading
import re
import asyncio
import logging
import argparse
import traceback
import json
from typing import Dict, Any, List, Callable, Pattern

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice as BleakDevice

import couchdb
from couchdb.mapping import Document, ListField, TextField, DictField, Mapping

from dataRep import DataRep



conn_flag = "0"
clients : List[BleakClient] = []
global_loop = ""

global client_address_order
client_address_order  = []
client_address_read_index = 0

global database
server = couchdb.Server()
database = server['gopro_stats']

for id in database:
 doc = database[id]
 database.delete(doc)
"""
class DataRep(Document):
 #data representation within couchdb, 1 "object" per client with MAC and actual data
 data = ListField(DictField(Mapping.build(address = TextField(), battery = TextField(), disk = TextField(), gps = TextField())))
"""

global dbdata
dbdata = DataRep()




class IdleState(State):

   def __init__(self):
    print("Switched to: ", str(self))


   def on_event(self, event):
       print("Event: ", event)
       global conn_flag

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
          asyncio.get_event_loop().run_until_complete(get_status(client,QUERY_REQ_UUID,query_event))
         return RecordingState()
        except Exception as ex:
         print("Exception in IdleSate.on_event(): \n", ex)

       if event == 'dms2':
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
         asyncio.get_event_loop().run_until_complete(get_status(client,QUERY_REQ_UUID,query_event))

        return IdleState()
       if event == 'dms1':
        self.count+=1

        return self

class ConnectingState(State):
      def __init__(self):
       print("Switched to: ", str(self))


      def on_event(self, event):
       if event == 'dms2':
        global query_event
        global response
        response=Response()
        query_event = asyncio.Event()

        def dummy_notification_handler(handle: int, data: bytes) -> None:
         print("dummy_notification_handler running")

         response.accumulate(data)
         if response.is_received:
           response.parse()
           global current_client
           global clients
           global dbdata
           global client_address_read_index
           try:
            
            compare_loop = global_loop
            asyncio.set_event_loop(compare_loop)
            asyncio.get_event_loop().gather(run_async_another_thread(compare_and_remove(dbdata, client_address_order, client_address_read_index, database)))
            """
            if not dbdata.id:
             dbdata.store(database)
            dbdata = DataRep.load(database, dbdata.id)

            if dbdata.data:
             for i in range(len(dbdata.data)): 
              print("Looking for: \n", client_address_order[client_address_read_index])
              if str(client_address_order[client_address_read_index]) == dbdata.data[i].address:
               dbdata.data.remove(dbdata.data[i])
               print("Removed: \n", str(dbdata.data[i]))
            """            
           except Exception as ex:
            print("Exception while trying to remove existing entries: \n", ex)

           try:
            
            upload_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(upload_loop)
            asyncio.get_event_loop().run_until_complete(run_async_another_thread(upload_data(clients, client_address_order,client_address_read_index, handle, QUERY_RSP_UUID, dbdata, response, database)))
            query_event.set()
            return

            """
            for t in clients:
             if t.address == client_address_order[client_address_read_index] and t.services.characteristics[handle].uuid == QUERY_RSP_UUID:
              dbdata.data.append(address = t.address, battery = response.data[70][0], disk = int.from_bytes(response.data[54], "big"), gps= response.data[68][0])
              dbdata.store(database)
              if client_address_read_index < (len(client_address_order)-1):
               client_address_read_index = client_address_read_index +1
              else:
               client_address_read_index = 0
             
            
              query_event.set()
              return
              """
           except Exception as ex:
            print("Exception while trying to upload data: \n", ex)
            print("Possibly useful data: \n", client_address_order, client_address_read_index)

        global clients
        global conn_flag

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
         global global_loop
         global_loop = asyncio.new_event_loop()
         asyncio.set_event_loop(global_loop)
         clients = asyncio.get_event_loop().run_until_complete(connect_ble(dummy_notification_handler, args.identifier))
         global client_address_order
         for u in clients:
          client_address_order.append(str(u.address))


         #now send a status subscription request query for each client to receive push notifications about the requested status
         address = QUERY_REQ_UUID
         for s in clients:
          asyncio.get_event_loop().run_until_complete(get_status(s,address,query_event))
         print("Client_address_order: \n", client_address_order)
        except Exception as ex:
         sys.exit("Connection failed, must restart program! Wait ...")

        conn_flag = "1"
        return IdleState()	
