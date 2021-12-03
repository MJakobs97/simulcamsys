# ble_connect.py/Open GoPro, Version 2.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# This copyright was auto-generated on Wed, Sep  1, 2021  5:05:56 PM

import re
import asyncio
import logging
import argparse
import time
from typing import Dict, Any, List, Callable, Pattern

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice as BleakDevice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

GOPRO_BASE_UUID = "b5f9{}-aa8d-11e3-9046-0002a5d5c51b"
GOPRO_BASE_URL = "http://10.5.5.9:8080"



async def connect_ble(
    notification_handler: Callable[[int, bytes], None], identifier: str = None
) -> BleakClient:
    """Connect to a GoPro, then pair, and enable notifications

    If identifier is None, the first discovered GoPro will be connected to.

    Args:
        notification_handler (Callable[[int, bytes], None]): callback when notification is received
        identifier (str, optional): Last 4 digits of GoPro serial number. Defaults to None.

    Returns:
        BleakClient: connected client
    """
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


async def main(identifier):
    def dummy_notification_handler(handle: int, data: bytes) -> None:
        ...

    clients = await connect_ble(dummy_notification_handler, identifier)

    COMMAND_REQ_UUID = GOPRO_BASE_UUID.format("0072")
    COMMAND_RSP_UUID = GOPRO_BASE_UUID.format("0073")
    SETTINGS_REQ_UUID = GOPRO_BASE_UUID.format("0074")
    SETTINGS_RSP_UUID = GOPRO_BASE_UUID.format("0075")

    for client in clients:
#     event.clear()
     await client.write_gatt_char(COMMAND_REQ_UUID, bytearray([3, 1, 1, 1]))
 #    await event.wait()
     #await client.disconnect()
    
    time.sleep(3)
    for client in clients: 
  #   event.clear()
     await client.write_gatt_char(COMMAND_REQ_UUID, bytearray([3, 1, 1, 0]))
   #  await event.wait()
    for client in clients: 
    # event.clear()
     await client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Connect to a GoPro camera, pair, then enable notifications.")
    parser.add_argument(
        "-i",
        "--identifier",
        type=str,
        help="Last 4 digits of GoPro serial number, which is the last 4 digits of the default camera SSID. \
            If not used, first discovered GoPro will be connected to",
        default=None,
    )
    args = parser.parse_args()

    asyncio.run(main(args.identifier))
