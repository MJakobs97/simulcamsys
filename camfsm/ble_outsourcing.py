import functools
import subprocess
import re
import asyncio
import logging
import time
import argparse
import sys
from typing import Dict, Any, List, Callable, Pattern
import concurrent.futures

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice as BleakDevice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except Exception as ex:
        #print("Exception in get_or_create_eventloop(): \n", str(ex))
        if "event loop" in str(ex):
            #print("Setting up a new one: \n")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop
            return asyncio.get_event_loop()

async def rec_start(client, address):
    try:
     await client.write_gatt_char(address, bytearray([3, 1, 1, 1]))
    except Exception as ex:
     print("Exception in rec_start: \n", ex)
     sys.exit("Rec_start failed, please await program restart!")

async def rec_stop(client, address):
    try:
     await asyncio.sleep(5)
     await client.write_gatt_char(address, bytearray([3, 1, 1, 0]))
    except Exception as ex:
     print("Exception in rec_stop: \n", ex)
     sys.exit("Rec_stop failed, please await program restart!")

async def rec_stop_threaded(client, address):
 try:
   with concurrent.futures.ProcessPoolExecutor() as pool:
    await asyncio.get_event_loop().run_in_executor(pool, functools.partial(rec_stop, client, address))
 except Exception as ex:
  print("Exception in rec_stop_threaded: \n", ex)

async def rec_start_all(clients, address):
 startliste = []
 for client in clients: 
  startliste.append(rec_start(client, address))
 res = await asyncio.gather(*startliste, return_exceptions=True)

async def rec_stop_all(clients, address):
 stopliste = []
 for client in clients:
  stopliste.append(rec_stop(client, address))
 res = await asyncio.gather(*stopliste, return_exceptions=True)


async def subscribe_status(client, address, query_event):
#send "subscribe" request for push notifications about
    BAT = 70 #int.bat% = 70
    GPS = 68 #gps_status = 68
    DSKSPC = 54 #remaining dskspc = 54
    VIDMIN = 35 #remaining minutes of capturing video with current settings = 35
#to queryID 0x93 = 0x53 + 1001 = 0x93
#queryID 0x53 works
#queryID 0x93 does not work at all, returns empty response
    try:
     print("Attempting to write_gatt_char")
     query_event.clear()
     await client.write_gatt_char(address, bytearray([0x05,0x53,BAT,GPS,DSKSPC, VIDMIN]))
     await query_event.wait()
     #task = asyncio.create_task(await_responses(query_event, 3))
     #while True:
      #await asyncio.sleep(5)
      #query_event.clear()
      #await query_event.wait()
    except Exception as ex:
     print("Exception in subscribe_status: \n", ex)
     sys.exit("Subscription failed \n")

async def get_status(client, address, query_event):
 BAT = 70
 GPS = 68
 DSKSPC = 54
 VIDMIN = 35

 try:
  query_event.clear()
  await client.write_gatt_char(address, bytearray([0x05, 0x13,BAT,GPS,DSKSPC,VIDMIN]))
  await query_event.wait()
 except Exception as ex:
  print("Exception in get_status: \n", ex)
  sys.exit("Gettin status failed \n")

async def await_responses(query_event,delay):
    try:
     while True:
      print("Awaiting response")
      #await asyncio.sleep(delay)
      query_event.clear()
      await query_event.wait()
    except Exception as ex:
     print("Exception in await_responses: \n", ex)
     sys.exit("Awaiting responses failed \n")



async def test_polling_response(client, address, poll_event):
    try:
     poll_event.clear()
     await client.write_gatt_char(address, bytearray([0x02,0x13,70]))
     await poll_event.wait()
     print("Poll_event: \n"+str(poll_event))
    except Exception as ex:
     print("Exception in test_polling_response: \n", ex)
     sys.exit("Testing polling failed \n")










async def connect_ble(notification_handler: Callable[[int, bytes], None], identifier: str = None) -> BleakClient:
   	    #DO NOT TOUCH THIS FUNCTION! IT IS WORKING AS EXPECTED!
            
            # Map of discovered devices indexed by name
            devices: Dict[str, BleakDevice] = {}

	    # Scan for devices
            logger.info(f"Scanning for bluetooth devices...")
	    # Scan callback to also catch nonconnectable scan responses
            def _scan_callback(device: BleakDevice, _: Any) -> None:
	        # Add to the dict if not unknown
                if device.name != "Unknown" and device.name is not None:
                    devices[device.name] = device

	    # Scan until we find devices
            matched_devices: List[BleakDevice] = []
            while len(matched_devices) == 0:
	        # Now get list of connectable advertisements
                
                #for device in asyncio.run(BleakScanner.discover(timeout=5, detection_callback=_scan_callback)):
                for device in await BleakScanner.discover(timeout=5, detection_callback=_scan_callback):
                    if device.name != "Unknown" and device.name is not None:
                        devices[device.name] = device
	        # Log every device we discovered
                for d in devices:
                    logger.info(f"\tDiscovered: {d}")
        	# Now look for our matching device(s)
                token = re.compile(r"GoPro [A-Z0-9]{4}" if identifier is None else f"GoPro {identifier}")
                matched_devices = [device for name, device in devices.items() if token.match(name)]
                logger.info(f"Found {len(matched_devices)} matching devices.")

	    # Connect to first matching Bluetooth device
            all_clients: List[BleakClient] = []

            for x in matched_devices:
             device = x 

	    #device = matched_devices[0]
             for attempt in range(10):
              logger.info(f"Establishing BLE connection to {device}...")
              client = BleakClient(device)
              try:
               await client.connect(timeout=20)
              except Exception as ex:
               #print("Exception: \n", ex)
               #raise
               continue
              break
             logger.info("BLE Connected!")

	     # Try to pair (on some OS's this will expectedly fail)
             logger.info("Attempting to pair...")
             for u in range(10):
              try:
               await client.pair()
              except NotImplementedError:
        	  #This is expected on Mac
               continue
              break
             logger.info("Pairing complete!")

	     # Enable notifications on all notifiable characteristics
             logger.info("Enabling notifications...")
             for service in client.services:
                 for char in service.characteristics:
                     if "notify" in char.properties:
                         logger.info(f"Enabling notification on char {char.uuid}")
                         await client.start_notify(char, notification_handler)

             logger.info("Done enabling notifications")
             all_clients.append(client)

            return all_clients
