CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/bin/activate"
conda activate keywordsearch
python3 main.py