#!/bin/bash

apt update -y && apt upgrade -y
apt install python3 -y
apt install pip3 -y

python -m pip install -r requirements.txt

cp goprofsm.service /etc/systemd/system/goprofsm.service
systemctl daemon-reload
systemctl start goprofsm.service
systemctl status goprofsm.service
systemctl enable goprofsm.service
systemctl status goprofsm.service