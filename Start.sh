#!/bin/bash

echo "==================================="
echo "Telegram Report Bot v5.0"
echo "==================================="

# Create required directories
mkdir -p data logs sessions

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Run bot
echo "Starting bot..."
python bot.py

echo "Bot stopped!"
