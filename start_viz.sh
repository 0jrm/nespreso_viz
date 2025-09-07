#!/bin/bash

# NeSPReSO Visualization Startup Script

# Set working directory
cd "$(dirname "$0")"

# Activate conda environment
echo "Activating nespreso conda environment..."
eval "$(/usr/bin/conda shell.bash hook)"
conda activate nespreso

# Set environment variables
export WSGI_MODE=true
export NESPRESO_VIZ_PATH=$(pwd)
export NESPRESO_VIZ_LOG=$(pwd)/logs/viz.log

# Create logs directory
mkdir -p logs

# Kill any existing processes
echo "Stopping existing processes..."
pkill -f "gunicorn.*wsgi:application" || true
pkill -f "python.*nespreso_viz.py" || true

# Wait a moment for processes to stop
sleep 2

# Test the WSGI application first
echo "Testing WSGI application..."
python -c "from wsgi import application; print('WSGI app loaded successfully')" || exit 1

# Start with gunicorn
echo "Starting NeSPReSO Visualization with Gunicorn..."
exec gunicorn -c config/gunicorn_viz.conf.py wsgi:application
