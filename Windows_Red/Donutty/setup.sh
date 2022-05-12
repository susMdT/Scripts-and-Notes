#!/bin/bash
cd /donut 
wget https://github.com/TheWover/donut/releases/download/v0.9.3/donut_v0.9.3.zip
unzip donut_v0.9.3.zip
chmod +x donut.exe
cd /donut/serv/
python3 /donut/serv/server.py