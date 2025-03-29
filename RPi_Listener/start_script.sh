#!/bin/bash

# Navigate to the project directory
cd ~/RPi_Listener/

# Activate the virtual environment
source venv_recorder/bin/activate

# Run the Python script
python Recorder_linux.py

# Optionally deactivate the virtual environment after the script finishes
deactivate