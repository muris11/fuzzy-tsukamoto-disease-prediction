# Alternative WSGI Configuration (if the main one fails)
import os
import sys

# Add project directory to sys.path
project_home = '/home/rifqy11/fuzzy-tsukamoto-disease-prediction'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ.setdefault('APP_NAME', 'Fuzzy Tsukamoto Diagnoser API')
os.environ.setdefault('WARNING_THRESHOLD', '60')
os.environ.setdefault('CORS_ORIGINS', '*')

# Import and create WSGI app
from api_app import app

# Use uvicorn's WSGI handler
from uvicorn.workers import WSGIWorker
application = app