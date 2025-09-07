#!/bin/bash

echo "=== NeSPReSO Visualization Status Check ==="
echo "Date: $(date)"
echo ""

echo "1. Checking if application is running..."
if ps aux | grep -E "(gunicorn.*wsgi:application)" | grep -v grep > /dev/null; then
    echo "✓ Gunicorn process found:"
    ps aux | grep -E "(gunicorn.*wsgi:application)" | grep -v grep
    echo ""
else
    echo "✗ No gunicorn process found for visualization"
    echo ""
fi

echo "2. Checking port 8050..."
if netstat -tlnp 2>/dev/null | grep :8050 > /dev/null; then
    echo "✓ Port 8050 is listening:"
    netstat -tlnp 2>/dev/null | grep :8050
    echo ""
else
    echo "✗ Port 8050 is not listening"
    echo ""
fi

echo "3. Testing local HTTP response..."
response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://146.201.220.16:8050/ 2>/dev/null)
if [ "$response" = "200" ]; then
    echo "✓ Application responds with HTTP 200"
else
    echo "✗ Application not responding properly (HTTP $response)"
fi
echo ""

echo "4. Checking recent logs..."
if [ -f "nespreso_viz.log" ]; then
    echo "Recent log entries:"
    tail -10 nespreso_viz.log
else
    echo "No log file found"
fi
echo ""

echo "5. Data directory status..."
if [ -d "/Net/work/ozavala/DATA/SubSurfaceFields/NeSPReSO" ]; then
    file_count=$(ls /Net/work/ozavala/DATA/SubSurfaceFields/NeSPReSO/*.nc 2>/dev/null | wc -l)
    echo "✓ Data directory accessible with $file_count NetCDF files"
else
    echo "✗ Data directory not accessible"
fi

echo ""
echo "=== Status Check Complete ==="
