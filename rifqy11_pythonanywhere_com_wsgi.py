# PythonAnywhere WSGI Configuration for Fuzzy Tsukamoto API
import os
import sys

# Add project directory to sys.path
project_home = '/home/rifqy11/fuzzy-tsukamoto-disease-prediction'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for PythonAnywhere
os.environ.setdefault('APP_NAME', 'Fuzzy Tsukamoto Diagnoser API')
os.environ.setdefault('WARNING_THRESHOLD', '60')
os.environ.setdefault('CORS_ORIGINS', '*')

# Import the FastAPI application
from api_app import app

# Convert FastAPI to WSGI using the standard approach
# This is the most reliable method for PythonAnywhere
from fastapi.middleware.wsgi import WSGIMiddleware

# Create WSGI application
application = WSGIMiddleware(app)