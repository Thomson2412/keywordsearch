# Keywordsearch
This project is created for the ViFrU.
The program can create transcriptions of wav and mp3 files by leveraging the latest Mozilla Deepspeech.
Transcriptions can be searched for entered keywords.
Abstracts and audio snipets of the found keywords can be extracted.

## Instalation

### Setup script
A setup script is provided to ease the instalation process.
However, this script is only tested on the Ubuntu Linux distro. Other Ubuntu based distributions might work but are not tested.
Operating systems besides Linux are not superted by the setup script.

The setup script will install miniconda, create a new conda enviroment, download the required dependencies and the required deepspeech models and will create a desktop entry.

To run the setup script use the following command:
```
./install
```

The program can take advandtaege of gpu acceleration.
Incase the system has a compatible NVIDIA gpu please pass the following agrumant to the install script:
```
./install --gpu
```

### Manual
If, for whatever reason, the setup script cannot be used, manual instalation can be performed with the follwing commands.

#### Miniconda instalation:
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O install_files/miniconda.sh
chmod +x miniconda.sh
./miniconda.sh
```

#### Downloading deepspeech models (execute in the root folder of the project):
```
mkdir -p data/models
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm -O data/models/deepspeech-0.9.3-models.pbmm
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer -O data/models/deepspeech-0.9.3-models.scorer
```

#### Creating conda enviroment:
```
conda env remove --name keywordsearch
conda create --name keywordsearch python=3.9
conda activate keywordsearch
```

#### Installing dependecies (execute in the root folder of the project with enviroment activated):
```
sudo apt install ffmpeg
sudo apt install gcc
sudo apt install portaudio19-dev
```

For usage without gpu acceleration use the following commands:
```
pip install .[cpu]
```

For usage with gpu acceleration use the following commands:
```
conda install cudatoolkit=10.1 cudnn=7.6
pip install .[gpu]
```



## Usage
Keywordsearch can be used with a GUI or via the CLI.

### GUI
To start the GUI use the desktop entry created by the setup script or use the following commands:
```
conda activate keywordsearch
python main.py
```

### CLI
To use the CLI make sure the enviroment is activaded with the following command:
```
conda activate keywordsearch
```

CLI usage:
```
python kwscli.py "FILES" --output "PATH TO OUTPUT FOLDER"
```
Example:
```
python kwscli.py input/test_file_1.mp3 input/test_file_2.wav --output output_folder/test_files/
```

