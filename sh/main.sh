#!/bin/bash

# Activate virtual environment
echo "Enter virtual environment name: "
read venv_name
source "$venv_name/bin/activate"
echo -e "\n"

# Run python script
python3 -m main.main

deactivate