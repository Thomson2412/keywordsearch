#!/bin/bash

python3 -m venv venv
pip isntall .
echo "[Desktop Entry]
Name=Keywordsearch
Exec=bash -c 'cd $(pwd); source venv/bin/activate; python3 main.py'
Type=Application" > $HOME/.local/share/applications/keywordsearch.desktop


