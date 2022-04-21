#!/bin/bash

sudo apt install python3-venv -y
sudo apt install python3-pip -y
sudo apt-get install python3-tk -y
python3 -m venv venv
source venv/bin/activate
pip install .
echo "[Desktop Entry]
Name=Keywordsearch
Exec=bash -c 'cd $(pwd); source venv/bin/activate; python3 main.py'
Type=Application" > $HOME/.local/share/applications/keywordsearch.desktop


