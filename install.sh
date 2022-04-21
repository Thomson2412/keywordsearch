#!/bin/bash

sudo apt install python3-venv
sudo apt install python3-pip
python3 -m venv venv
pip install .
echo "[Desktop Entry]
Name=Keywordsearch
Exec=bash -c 'cd $(pwd); source venv/bin/activate; python3 main.py'
Type=Application" > $HOME/.local/share/applications/keywordsearch.desktop


