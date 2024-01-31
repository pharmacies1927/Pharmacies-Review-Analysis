#!/bin/bash

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt


echo "Setup completed. To run the Streamlit app, use 'streamlit run app.py' or refer to readme.md file."
