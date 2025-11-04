"""
Xweather API client for fetching hyperlocal weather data.
"""
import requests
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Optional, Tuple
from cachetools import TTLCache
import time
import logging
from config import (
    XWEATHER_CLIENT_ID, 
    XWEATHER_CLIENT_SECRET,
    XWEATHER_BASE_URL, 
    FORECAST_ENDPOINT, 
    OBSERVATIONS_ENDPOINT,
    CACHE_TTL,
    MAX_CACHE_SIZE
)
from requests.adapters import HTTPAdapter, Retry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XweatherClient:
    """
    Client for interacting with the Xweather API to fetch hyperlocal weather data.
    """
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Initialize the Xweather client.
        
        Args:
            client_id: Xweather client ID. If None, will use from config.
            client_secret: Xweather client secret. If None, will use from config.
        """
        self.client_id = client_id or XWEATHER_CLIENT_ID
        self.client_secret = client_secret or XWEATHER_CLIENT_SECRET
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Both Xweather client ID and client secret are required")
        
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504, 429])
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        self.session.headers.update({
            'User-Agent': 'HyperlocalWeatherMap/1.0'
        })
        
        # Initialize cache
        self.cache = TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL)
        
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Make a request to the Xweather API with caching.
        
        Args:
            endpoint: API endpoint URL
            params: Request parameters
            
        Returns:
            JSON response data
        """
        # Add API credentials to parameters
        params['client_id'] = self.client_id
        params['client_secret'] = self.client_secret
        
        # Create cache key
        cache_key = f"{endpoint}_{hash(frozenset(params.items()))}"
        
        # Check cache first
        if cache_key in self.cache:
            logger.info("Returning cached data")
            return self.cache[cache_key]
        
        try:
            logger.info(f"Making request to {endpoint}")
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            self.cache[cache_key] = data
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_observations(self, lat: float, lon: float, radius: int = 50) -> pd.DataFrame:
        """
        Get current weather observations for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in kilometers
            
        Returns:
            DataFrame with observation data
        """
        endpoint = f"{OBSERVATIONS_ENDPOINT}/{lat},{lon}"
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'radius': f"{radius}km",
            'limit': 100
        }
        
        data = self._make_request(endpoint, params)
        
        if not data.get('success'):
            raise ValueError(f"API error: {data.get('error', {}).get('description', 'Unknown error')}")
        
        observations = data.get('response', [])
        
        if not observations:
            logger.warning("No observations found")
            return pd.DataFrame()
        
        # Extract relevant data
        obs_data = []
        for obs in observations:
            obs_data.append({
                'latitude': obs.get('loc', {}).get('lat'),
                'longitude': obs.get('loc', {}).get('long'),
                'station_id': obs.get('id'),
                'name': obs.get('place', {}).get('name'),
                'temperature': obs.get('ob', {}).get('tempF'),
                'humidity': obs.get('ob', {}).get('humidity'),
                'pressure': obs.get('ob', {}).get('pressureIN'),
                'wind_speed': obs.get('ob', {}).get('windSpeedMPH'),
                'wind_direction': obs.get('ob', {}).get('windDir'),
                'weather': obs.get('ob', {}).get('weather'),
                'timestamp': obs.get('ob', {}).get('dateTimeISO')
            })
        
        df = pd.DataFrame(obs_data)
        
        # Convert to GeoDataFrame
        if not df.empty:
            gdf = gpd.GeoDataFrame(
                df, 
                geometry=gpd.points_from_xy(df.longitude, df.latitude),
                crs='EPSG:4326'
            )
            return gdf
        
        return pd.DataFrame()
    
    def get_forecast(self, lat: float, lon: float, days: int = 5) -> pd.DataFrame:
        """
        Get weather forecast for a location using path-style endpoint.
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of forecast days (max 15)
            
        Returns:
            DataFrame with forecast data
        """
        endpoint = f"{FORECAST_ENDPOINT}/{lat},{lon}"
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'limit': days
        }
        
        data = self._make_request(endpoint, params)
        
        if not data.get('success'):
            raise ValueError(f"API error: {data.get('error', {}).get('description', 'Unknown error')}")
        
        periods = data.get('response', [{}])[0].get('periods', [])
        
        if not periods:
            logger.warning("No forecast data found")
            return pd.DataFrame()
        
        # Extract forecast data
        forecast_data = []
        for period in periods:
            forecast_data.append({
                'latitude': lat,
                'longitude': lon,
                'datetime': period.get('dateTimeISO'),
                'temperature_max': period.get('maxTempF'),
                'temperature_min': period.get('minTempF'),
                'humidity': period.get('humidity'),
                'pressure': period.get('pressureIN'),
                'wind_speed': period.get('windSpeedMPH'),
                'wind_direction': period.get('windDir'),
                'weather': period.get('weather'),
                'precip_probability': period.get('precipIN'),
                'snow_probability': period.get('snowIN')
            })
        
        df = pd.DataFrame(forecast_data)
        
        # Convert to GeoDataFrame
        if not df.empty:
            gdf = gpd.GeoDataFrame(
                df, 
                geometry=gpd.points_from_xy(df.longitude, df.latitude),
                crs='EPSG:4326'
            )
            return gdf
        
        return pd.DataFrame()
    
    def get_hyperlocal_data(self, center_lat: float, center_lon: float, 
                          radius: int = 50, include_forecast: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get comprehensive hyperlocal weather data including observations and forecast.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius: Search radius in kilometers
            include_forecast: Whether to include forecast data
            
        Returns:
            Tuple of (observations_df, forecast_df)
        """
        logger.info(f"Fetching hyperlocal data for {center_lat}, {center_lon}")
        
        # Get observations
        observations = self.get_observations(center_lat, center_lon, radius)
        
        # Get forecast if requested
        forecast = pd.DataFrame()
        if include_forecast:
            forecast = self.get_forecast(center_lat, center_lon)
        
        return observations, forecast
