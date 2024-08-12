#!/bin/bash

if [ -n "$TAIDE_API_KEY" ]; then
    echo "TAIDE_API_KEY detected, running app/app_taide.py..."
    poetry run python app/app_taide.py
elif [ -n "$NVIDIA_API_KEY" ]; then
    echo "NVIDIA_API_KEY detected, running app/app_nvidia.py..."
    poetry run python app/app_nvidia.py
else
    echo "No API key provided. Container will keep running."
    tail -f /dev/null
fi
