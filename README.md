# Simulcamsys #

A python-based command line application intended to provide automated BLE connectivity and simultaneous shutter control over multiple GoPro cameras.
Developed to make use of a raspberry pi's GPIO-pins to react to momentary buttons as well as one 5v line input, for use on other systems this input handling should be adjusted.
Draws inspiration from the officially provided [tutorials](https://gopro.github.io/OpenGoPro/tutorials/ "Title").

## Legal disclaimer ##

This product and/or service is not affiliated with, endorsed by or in any way associated with GoPro Inc. or its products and services. 
GoPro, HERO, and their respective logos are trademarks or registered trademarks of GoPro, Inc.

## Requirements / materials ##

* A raspberry pi model 3b+ (or newer), set up to the current standards (python3.9.2). Enabling ssh is required for initial configuration.
* The GoPros intended to be connected (currently officially supports Hero 9 Black only)
* At least two momentary switches
* An external input voltage used to trigger the shutter control. In lieu of one, consider using a 3v3 pin with the corresponding switch.
	* **IMPORTANT**: please regulate any input above 3.3v down to somewhere around 2.5-3v and limit its current to a maximum of 10mA to avoid frying the pi
* Jumper cables / wires to fit your needs / enclosure
* **Optional**: logic level converter or enough resistors to solder a loaded voltage divider

## Pinout / wiring ##

* External trigger voltage -> momentary switch -> GPIO 4
* GPIO 3 -> momentary button -> GND

## Useage ##

1. Run "smController.py"
2. Optionally turn on the auditory feedback 'BEEP' on every camera
3. Set your GoPro cameras into BLE advertising mode 
	1. Navigate to CONNECTIONS
	2. Set "Wireles Connections" to 'On'
	3. Navigate to CONNECT DEVICE
	4. Choose "Quick App"
4. While the application is running and in 'IdleState' press and hold down the momentary button thats connected to GPIO 3 for 1s to switch to 'ConnectingState'.
5. Press and hold the same button again for 1s to initiate the connection process. Once done, the application returns to 'IdleState'.
6. Now every connected GoPro's shutter can be controlled by holding down the momentary switch connected to GPIO 4, switching to application to 'RecordingState' and starting the recording on every connected camera. Letting go of that switch stops the recording and returns the application to 'IdleState'.
	1. Due to the nature of asynchronous programming a small but inconsequential delay between each camera is to be expected

7. Optionally create a new systemd service to run "smController.py" on startup (with restart on failure or unexpected termination) to eliminate the need for external interaction.

## Troubleshooting ##

Error | Solution
------|---------
Python related error messages | Install the most recent version of python and pip, then install missing modules
Software caused connection abort | Turn off the 'Wireless Connection' option on each camera, then restart the application (or wait for it to restart in case of Useage.7), then refer back to [Useage](#Useage "Goto Useage")
Noticeable delay between cameras | Currently not a bug, it's caused by database accesses



