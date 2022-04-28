#!/bin/bash

sudo apt install python3-venv -y
sudo apt install python3-pip -y
sudo apt-get install python3-tk -y
python3 -m venv venv
source venv/bin/activate
pip install .
rm -rf data/models
mkdir -p data/models
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm -O data/models/deepspeech-0.9.3-models.pbmm
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer -O data/models/deepspeech-0.9.3-models.scorer
echo "[Desktop Entry]
Name=Keywordsearch
Exec=bash -c 'cd $(pwd); source venv/bin/activate; python3 main.py'
Type=Application" > $HOME/Desktop/keywordsearch.desktop


