# Vercel API Handler for Fuzzy Tsukamoto Disease Prediction
import os
from api_app import app

# Set environment variables for Vercel
os.environ.setdefault('APP_NAME', 'Fuzzy Tsukamoto Diagnoser API')
os.environ.setdefault('WARNING_THRESHOLD', '60')
os.environ.setdefault('CORS_ORIGINS', '*')

# For Vercel, export the FastAPI app directly
# Vercel supports ASGI applications natively
app = app