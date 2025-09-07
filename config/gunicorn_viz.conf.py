#!/usr/bin/env python3
"""
Gunicorn configuration file for NeSPReSO Visualization
"""

# Server socket
bind = "0.0.0.0:8050"
backlog = 2048

# Worker processes
workers = 1  # Dash apps work better with fewer workers
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True  # Important for Dash apps

# Timeouts
timeout = 1800  # 30 minutes for large data processing
keepalive = 2
graceful_timeout = 30
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "nespreso_viz"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Memory management
max_requests = 500  # Restart workers more frequently for memory management
max_requests_jitter = 50
