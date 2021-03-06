from state import State
from ble_outsourcing import connect_ble, get_status, rec_stop_all, rec_start_all
from notification_outsourcing import run_compare_threaded, run_upload_threaded
from response import Response


import os
import sys
import asyncio
import nest_asyncio
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
         address = COMMAND_REQ_UUID
         global global_loop
         start_loop = global_loop
         asyncio.set_event_loop(start_loop)
         asyncio.get_event_loop().run_until_complete(rec_start_all(clients, address))

         for client in clients:
          #----COROUTINE GETS CALLED----
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
        address = COMMAND_REQ_UUID  
        global global_loop
        stop_loop = global_loop
        #nest_asyncio.apply(stop_loop)
        asyncio.set_event_loop(stop_loop)
        asyncio.get_event_loop().run_until_complete(rec_stop_all(clients, address))

        for client in clients:
         #----COROUTINE GETS CALLED----
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
           print("Response: \n", response)
           global current_client
           global clients
           global dbdata
           global client_address_read_index
           try:
            global global_loop
            compare_loop = global_loop
            nest_asyncio.apply(compare_loop)
            asyncio.set_event_loop(compare_loop)            
            data_modified = asyncio.get_event_loop().run_until_complete(run_compare_threaded(dbdata, client_address_order, client_address_read_index, database))
            if type(data_modified) == DataRep:
             dbdata = data_modified       
           except Exception as ex:
            print("Exception while trying to remove existing entries: \n", ex)

           try:
            
            upload_loop = global_loop
            nest_asyncio.apply(upload_loop)
            asyncio.set_event_loop(upload_loop)
            index = asyncio.get_event_loop().run_until_complete(run_upload_threaded(clients, client_address_order,client_address_read_index, handle, QUERY_RSP_UUID, dbdata, response, database))
            #print("address_read_index in statesimpl after upload: \n", index)
            if type(index) == int:
             client_address_read_index = index
            query_event.set()
            return
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
