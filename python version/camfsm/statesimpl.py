from state import State
import subprocess

class IdleState(State):

    def on_event(self, event):

       if event == 'dms1':
	for client in clients:
	 await client.write_gatt_char(COMMAND_REQ_UUID, bytearray([3, 1, 1, 1]))
       return RecordingState()
       
       if event == 'dms2':
       return ConnectingState()

       return self



class RecordingState(State):
    
    def on_event(self, event):
        if event == 'dms0':
	 for client in clients:
	  await client.write_gatt_char(COMMAND_REQ_UUID, bytearray([3, 1, 1, 0]))
        return IdleState()
        if event == 'dms1':
            print(self.count)
            self.count+=1

        return self
    

class ConnectingState(State):
	
    
	

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

    def __init__(self):

     def dummy_notification_handler(handle: int, data: bytes) -> None:
        ...
     global clients = await connect_ble(dummy_notification_handler, identifier)

     return IdleState()