echo "Setting up Python virtual environment for Jupyter Notebooks ..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source .venv/bin/activate
# Install dependencies
pip install -r requirements.txt

echo ""
echo "Setup complete! Virtual environment created and dependencies installed."
echo "Virtual environment is now ACTIVE in your current shell."
echo ""
echo "To deactivate later, run: deactivate"
echo "To activate in a new shell, run: source .venv/bin/activate"
