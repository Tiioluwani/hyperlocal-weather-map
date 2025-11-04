"""
Data processing utilities for hyperlocal weather data.
"""
import pandas as pd
import geopandas as gpd
import numpy as np
from typing import Dict, List, Optional, Tuple
from shapely.geometry import Point
import logging

logger = logging.getLogger(__name__)

class WeatherDataProcessor:
    """
    Process and structure weather data for geospatial visualization.
    """
    
    def __init__(self):
        """Initialize the data processor."""
        self.weather_icons = {
            'clear': '☀️',
            'sunny': '☀️',
            'partly cloudy': '⛅',
            'cloudy': '☁️',
            'overcast': '☁️',
            'rain': '🌧️',
            'showers': '🌦️',
            'thunderstorm': '⛈️',
            'snow': '❄️',
            'fog': '🌫️',
            'haze': '🌫️'
        }
    
    def clean_weather_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate weather data.
        
        Args:
            df: Raw weather DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        # Remove rows with missing coordinates
        df = df.dropna(subset=['latitude', 'longitude'])
        
        # Convert temperature to numeric, handling missing values
        if 'temperature' in df.columns:
            df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
        
        if 'temperature_max' in df.columns:
            df['temperature_max'] = pd.to_numeric(df['temperature_max'], errors='coerce')
        
        if 'temperature_min' in df.columns:
            df['temperature_min'] = pd.to_numeric(df['temperature_min'], errors='coerce')
        
        # Convert humidity to numeric
        if 'humidity' in df.columns:
            df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
        
        # Convert pressure to numeric
        if 'pressure' in df.columns:
            df['pressure'] = pd.to_numeric(df['pressure'], errors='coerce')
        
        # Convert wind speed to numeric
        if 'wind_speed' in df.columns:
            df['wind_speed'] = pd.to_numeric(df['wind_speed'], errors='coerce')
        
        # Standardize weather descriptions
        if 'weather' in df.columns:
            df['weather'] = df['weather'].str.lower().str.strip()
            df['weather_icon'] = df['weather'].map(self.weather_icons).fillna('🌤️')
        
        # Add temperature categories
        if 'temperature' in df.columns:
            df['temp_category'] = pd.cut(
                df['temperature'], 
                bins=[-np.inf, 32, 50, 70, 90, np.inf],
                labels=['Freezing', 'Cold', 'Cool', 'Warm', 'Hot']
            )
        
        return df
    
    def create_heatmap_data(self, df: pd.DataFrame, 
                          lat_col: str = 'latitude', 
                          lon_col: str = 'longitude',
                          value_col: str = 'temperature') -> List[Tuple[float, float, float]]:
        """
        Create heatmap data for visualization.
        
        Args:
            df: DataFrame with weather data
            lat_col: Latitude column name
            lon_col: Longitude column name
            value_col: Value column for heatmap intensity
            
        Returns:
            List of (lat, lon, value) tuples
        """
        if df.empty:
            return []
        
        # Remove rows with missing values
        heatmap_data = df[[lat_col, lon_col, value_col]].dropna()
        
        return [(row[lat_col], row[lon_col], row[value_col]) 
                for _, row in heatmap_data.iterrows()]
    
    def aggregate_by_grid(self, df: pd.DataFrame, grid_size: float = 0.01) -> gpd.GeoDataFrame:
        """
        Aggregate weather data by grid cells.
        
        Args:
            df: Weather DataFrame
            grid_size: Grid cell size in degrees
            
        Returns:
            GeoDataFrame with aggregated data
        """
        if df.empty:
            return gpd.GeoDataFrame()
        
        # Create grid cells
        df['grid_lat'] = (df['latitude'] // grid_size) * grid_size
        df['grid_lon'] = (df['longitude'] // grid_size) * grid_size
        
        # Aggregate by grid
        agg_data = df.groupby(['grid_lat', 'grid_lon']).agg({
            'temperature': ['mean', 'min', 'max', 'count'],
            'humidity': 'mean',
            'pressure': 'mean',
            'wind_speed': 'mean'
        }).reset_index()
        
        # Flatten column names
        agg_data.columns = ['grid_lat', 'grid_lon', 'temp_mean', 'temp_min', 
                          'temp_max', 'station_count', 'humidity_mean', 
                          'pressure_mean', 'wind_speed_mean']
        
        # Create geometry for grid cells
        agg_data['geometry'] = [
            Point(lon, lat) for lat, lon in zip(agg_data['grid_lat'], agg_data['grid_lon'])
        ]
        
        # Convert to GeoDataFrame
        gdf = gpd.GeoDataFrame(agg_data, crs='EPSG:4326')
        
        return gdf
    
    def calculate_weather_gradients(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate temperature and pressure gradients.
        
        Args:
            df: Weather DataFrame
            
        Returns:
            DataFrame with gradient calculations
        """
        if df.empty or len(df) < 2:
            return df
        
        # Calculate distances between points
        from scipy.spatial.distance import pdist, squareform
        from scipy.spatial.distance import cdist
        
        coords = df[['latitude', 'longitude']].values
        distances = cdist(coords, coords, metric='euclidean')
        
        # Calculate temperature gradients
        if 'temperature' in df.columns:
            temp_gradients = []
            for i in range(len(df)):
                # Find nearest neighbors
                nearest_indices = np.argsort(distances[i])[1:4]  # Skip self, get 3 nearest
                
                if len(nearest_indices) > 0:
                    temp_diff = df.iloc[i]['temperature'] - df.iloc[nearest_indices]['temperature'].mean()
                    distance = distances[i][nearest_indices].mean()
                    gradient = temp_diff / distance if distance > 0 else 0
                    temp_gradients.append(gradient)
                else:
                    temp_gradients.append(0)
            
            df['temperature_gradient'] = temp_gradients
        
        return df
    
    def create_weather_zones(self, df: pd.DataFrame, 
                           temp_threshold: float = 5.0) -> gpd.GeoDataFrame:
        """
        Create weather zones based on temperature differences.
        
        Args:
            df: Weather DataFrame
            temp_threshold: Temperature difference threshold for zones
            
        Returns:
            GeoDataFrame with weather zones
        """
        if df.empty:
            return gpd.GeoDataFrame()
        
        # Calculate temperature statistics
        temp_mean = df['temperature'].mean()
        temp_std = df['temperature'].std()
        
        # Create temperature zones
        df['temp_zone'] = pd.cut(
            df['temperature'],
            bins=[-np.inf, temp_mean - temp_std, temp_mean + temp_std, np.inf],
            labels=['Cold Zone', 'Moderate Zone', 'Warm Zone']
        )
        
        # Group by temperature zone
        zones = df.groupby('temp_zone', observed=True).agg({
            'latitude': ['mean', 'count'],
            'longitude': 'mean',
            'temperature': ['mean', 'min', 'max'],
            'humidity': 'mean',
            'pressure': 'mean'
        }).reset_index()
        
        # Flatten column names
        zones.columns = ['zone', 'lat_mean', 'station_count', 'lon_mean', 
                        'temp_mean', 'temp_min', 'temp_max', 'humidity_mean', 'pressure_mean']
        
        # Create geometry
        zones['geometry'] = [Point(lon, lat) for lat, lon in zip(zones['lat_mean'], zones['lon_mean'])]
        
        # Convert to GeoDataFrame
        zones_gdf = gpd.GeoDataFrame(zones, crs='EPSG:4326')
        
        return zones_gdf
    
    def prepare_for_mapping(self, observations: pd.DataFrame, 
                          forecast: pd.DataFrame = None) -> Dict[str, gpd.GeoDataFrame]:
        """
        Prepare weather data for mapping visualization.
        
        Args:
            observations: Observations DataFrame
            forecast: Forecast DataFrame (optional)
            
        Returns:
            Dictionary with processed data for mapping
        """
        result = {}
        
        # Process observations
        if not observations.empty:
            obs_clean = self.clean_weather_data(observations)
            result['observations'] = obs_clean
            
            # Create aggregated grid data
            result['grid_data'] = self.aggregate_by_grid(obs_clean)
            
            # Create weather zones
            result['weather_zones'] = self.create_weather_zones(obs_clean)
            
            # Calculate gradients
            result['gradients'] = self.calculate_weather_gradients(obs_clean)
        
        # Process forecast
        if forecast is not None and not forecast.empty:
            forecast_clean = self.clean_weather_data(forecast)
            result['forecast'] = forecast_clean
        
        return result
