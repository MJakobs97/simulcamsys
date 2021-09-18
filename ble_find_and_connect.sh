#!/bin/sh

DIRECTORY="/tmp_storage"
FILE_found_dev="/tmp_storage/found_devices.txt"
FILE_isolated_mac="/tmp_storage/isolated_mac.txt"

if [ -d "$DIRECTORY" ]; then
	#this may require authentication if not run with sudo
	mkdir tmp_storage
	touch tmp_storage/found_devices.txt
	touch tmp_storage/isolated_mac.txt
	echo "DNF - required data structure created!"
fi

echo "ble scan on"
bluetoothctl --scan on & > /dev/null
sleep 10
bluetoothctl --scan off & > /dev/null
echo "ble scan off"

bluetoothctl -- devices >> tmp_storage/found_devices.txt
sleep 5 && echo "finished scanning"

#grep out the mac address from "Device [MacAddress] [Identifier]" and store in file
grep -iEo '([[:space:]][a-fA-F0-9]{2})([ :-]([a-fA-F0-9]{2})){5}' tmp_storage/found_devices.txt >> tmp_storage/isolated_mac.txt

echo "trust & pairing - routine running"
let counter=0

#iterate over all MAC's to trust, pair & connect devices
while IFS= read -r line; do 
	echo $counter
	bluetoothctl -- trust $line & > /dev/null
	sleep 5
	bluetoothctl -- paur $line & > /dev/null
	sleep 5
	bluetoothctl -- connect $line & > /dev/null
	let counter++
done < tmp_storage/isolated_mac.txt

echo "$counter devices paired"

echo "The following devices have been connected: "
	bluetoothctl -- devices
	sleep 5

let counter2=0

while IFS= read -r line2; do
	echo $line2 to be removed
	sleep3
	bluetoothctl -- remove $line2
	sleep 1
	let counter2++
	echo "$line2 removed"
done < tmp_storage/isolated_mac.txt

echo "$counter2 devices removed"

#creating list of mac addresses to use with gopro-ble-py
address_list=" "

while IFS= read -r line3; do
	address_list+=$line3,
done < tmp_storage/isolated_mac.txt

#remove last "," from list
address_list=${address_list::-1}

echo $address_list

> tmp_storage/isolated_mac.txt
> tmp_storage/found_devices.txt
