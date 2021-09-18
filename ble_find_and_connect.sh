#!/bin/sh

echo "ble scan on"
bluetoothctl --scan on & > /dev/null
sleep 10
bluetoothctl --scan off & > /dev/null
echo "ble scan off"

bluetoothctl -- devices >> tmp_storage/found_devices.txt
sleep 5 && echo "finished scanning"
