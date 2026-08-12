


set -e  # stop on first error
 
echo "=== Loading modules ==="
module purge
module load python-miniconda3/4.12.0
module load gcc/11.2.0
 
echo "=== Creating virtual environment ==="
python -m venv venv
source venv/bin/activate
 
echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt
 
echo "=== Rebuilding C++ pybind11 extension (Linux build -- Windows .pyd will NOT work here) ==="
python setup.py build_ext --inplace
 
echo "=== Verifying import ==="
python -c "from src.structures import graph_decimate_kernel; print('OK:', graph_decimate_kernel.__file__)"
 
echo "=== Creating logs directory for Slurm output ==="
mkdir -p logs
 
echo ""
echo "=== Setup complete ==="
echo "Use 'source venv/bin/activate' in every future session before running anything."