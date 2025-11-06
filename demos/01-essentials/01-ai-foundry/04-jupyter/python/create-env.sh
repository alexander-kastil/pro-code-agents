#!/bin/bash
# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt