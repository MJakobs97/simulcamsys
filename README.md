# Simulcamsys #

A python-based application intended to provide automated BLE connectivity and simultaneous shutter control over multiple GoPro cameras.
Developed to make use of a raspberry pi's GPIO-pins to react to momentary buttons as well as one 5v line input, for use on other systems this input handling should be adjusted.

## Legal disclaimer ##

This product and/or service is not affiliated with, endorsed by or in any way associated with GoPro Inc. or its products and services. 
GoPro, HERO, and their respective logos are trademarks or registered trademarks of GoPro, Inc.

## Requirements materials ##

* A raspberry pi model 3b+ (or newer), set up to the current standards. Enabling ssh is required for initial configuration.
* At least one momentary switch
* An external input voltage used to trigger the shutter control. In lieu of one, consider using a 3v3 pin with another button in between.
	* IMPORTANT: please regulate any input above 3.3v down to somewhere around 2.5-3v and limit its current to a maximum of 10mA to avoid frying the pi
* Jumper cables / wires to fit your needs / enclosure