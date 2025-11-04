"""
Configuration settings for the hyperlocal weather map application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Xweather API Configuration
XWEATHER_CLIENT_ID = os.getenv('XWEATHER_CLIENT_ID')
XWEATHER_CLIENT_SECRET = os.getenv('XWEATHER_CLIENT_SECRET')
XWEATHER_BASE_URL = os.getenv('XWEATHER_BASE_URL', 'https://data.api.xweather.com')

# Authenticated Map Tiles
if XWEATHER_CLIENT_ID and XWEATHER_CLIENT_SECRET:
    MAP_TILES_BASE_URL = f"https://maps.api.xweather.com/{XWEATHER_CLIENT_ID}_{XWEATHER_CLIENT_SECRET}"
else:
    MAP_TILES_BASE_URL = "https://maps.api.xweather.com"

# API Endpoints
FORECAST_ENDPOINT = f"{XWEATHER_BASE_URL}/forecasts"
OBSERVATIONS_ENDPOINT = f"{XWEATHER_BASE_URL}/observations"

# Cache settings
CACHE_TTL = 300  # 5 minutes in seconds
MAX_CACHE_SIZE = 1000

# Map settings
DEFAULT_ZOOM = 10
DEFAULT_CENTER = [40.7128, -74.0060]  # New York City coordinates

# Weather data settings
DEFAULT_RADIUS = 50  # km
MAX_POINTS = 1000
