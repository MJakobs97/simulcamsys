import subprocess
import re
import asyncio
import logging
import time
import argparse
from typing import Dict, Any, List, Callable, Pattern

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice as BleakDevice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        print(ex)
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_running_loop()

async def force_client_connect(c):
    #loop = get_or_create_eventloop()
    #loop.run(c.connect())
    await c.connect(timeout=15)

async def force_client_pair(c):
    #loop = get_or_create_eventloop()
    #loop.run(c.pair())
    await c.pair()

async def rec_start(client, address):
    await client.write_gatt_char(address, bytearray([3, 1, 1, 1]))

async def rec_stop(client, address):
    await client.write_gatt_char(address, bytearray([3, 1, 1, 0]))


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

             logger.info(f"Establishing BLE connection to {device}...")
             client = BleakClient(device)
             await client.connect(timeout=15)

             logger.info("BLE Connected!")

	     # Try to pair (on some OS's this will expectedly fail)
             logger.info("Attempting to pair...")
             try:
                 await client.pair()
             except NotImplementedError:
        	 # This is expected on Mac
                 pass
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
