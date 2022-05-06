#!/bin/bash

conda_dir=$HOME/miniconda3

mkdir install_files
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O install_files/miniconda.sh
chmod +x install_files/miniconda.sh
rm -rf ${conda_dir}
./install_files/miniconda.sh -b -p "${conda_dir}"

conda_cmd="${conda_dir}/bin/conda"
${conda_cmd} init
source "$HOME/.bashrc"
source "${conda_dir}/bin/activate"
conda config --set auto_activate_base false

export CONDA_ALWAYS_YES="true"
conda env remove --name keywordsearch
conda create --name keywordsearch python=3.8
conda activate keywordsearch
if [[ $CONDA_DEFAULT_ENV == "keywordsearch" ]]; then
  sudo apt install gcc -y
  sudo apt install portaudio19-dev -y
  conda install cudatoolkit=10.1 cudnn=7.6
  pip install .
    
  conda deactivate
  conda deactivate
    
  rm -rf data/models
  mkdir -p data/models
  wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm -O data/models/deepspeech-0.9.3-models.pbmm
  wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer -O data/models/deepspeech-0.9.3-models.scorer

  echo "[Desktop Entry]
Name=Keywordsearch
Exec=bash -c 'cd $(pwd); source ${conda_dir}/bin/activate; conda activate keywordsearch; python3 main.py'
Type=Application" | sudo tee /usr/share/applications/keywordsearch.desktop
    
fi
unset CONDA_ALWAYS_YES


