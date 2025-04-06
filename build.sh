#!/bin/bash
# Install system dependencies
apt-get update && apt-get install -y libfreetype6-dev

# Install Python dependencies
pip install -r requirements.txt
