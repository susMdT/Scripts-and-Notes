#!/bin/bash
apt update ; apt install subversion python3 python-pip -y
svn export 'https://github.com/susMdT/Scripts-and-Notes/trunk/Custom Vulnapps/Swift Vulnlabs Flaskapp'
pip install flask
mv 'Swift Vulnlabs Flaskapp' flaskapp
cd flaskapp ; env WERKZEUG_DEBUG_PIN=off python3 app.py
