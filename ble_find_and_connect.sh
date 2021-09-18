#!/bin/sh

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
