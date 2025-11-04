"""
Main application for hyperlocal weather map.
"""
import os
import sys
import logging
from typing import Dict, Tuple
import pandas as pd
import geopandas as gpd
import requests

from xweather_client import XweatherClient
from data_processor import WeatherDataProcessor
from weather_map import WeatherMap
from config import XWEATHER_CLIENT_ID, XWEATHER_CLIENT_SECRET

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HyperlocalWeatherApp:
    """
    Main application class for hyperlocal weather mapping.
    """
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Initialize the application.
        
        Args:
            client_id: Xweather client ID
            client_secret: Xweather client secret
        """
        self.client_id = client_id or XWEATHER_CLIENT_ID
        self.client_secret = client_secret or XWEATHER_CLIENT_SECRET
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Both Xweather client ID and client secret are required. Set XWEATHER_CLIENT_ID and XWEATHER_CLIENT_SECRET environment variables.")
        
        # Initialize components
        self.client = XweatherClient(self.client_id, self.client_secret)
        self.processor = WeatherDataProcessor()
        self.map_builder = WeatherMap()
        
        logger.info("Hyperlocal Weather App initialized")
    
    def get_weather_data(self, center_lat: float, center_lon: float, 
                        radius: int = 50, include_forecast: bool = True) -> Dict:
        """
        Fetch and process weather data for a location.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius: Search radius in kilometers
            include_forecast: Whether to include forecast data
            
        Returns:
            Dictionary with processed weather data
        """
        logger.info(f"Fetching weather data for {center_lat}, {center_lon}")
        
        try:
            # Get raw data from API
            observations, forecast = self.client.get_hyperlocal_data(
                center_lat, center_lon, radius, include_forecast
            )
            
            # Process the data
            processed_data = self.processor.prepare_for_mapping(observations, forecast)
            
            logger.info(f"Retrieved {len(observations)} observations")
            if not forecast.empty:
                logger.info(f"Retrieved {len(forecast)} forecast periods")
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            raise
    
    def create_weather_map(self, weather_data: Dict, 
                          output_file: str = 'weather_map.html',
                          tile_layer: str = 'satellite',
                          auto_open: bool = True) -> str:
        """
        Create and save a weather map.
        
        Args:
            weather_data: Processed weather data
            output_file: Output HTML file path
            tile_layer: Base tile layer to use
            auto_open: Whether to automatically open in browser
            
        Returns:
            Path to saved map file
        """
        logger.info("Creating weather map")
        
        try:
            # Create comprehensive map
            map_obj = self.map_builder.create_comprehensive_map(
                weather_data,
                tile_layer=tile_layer,
                show_heatmap=True,
                show_zones=True,
                show_overlays=True
            )
            
            # Save map
            self.map_builder.save_map(map_obj, output_file, auto_open=auto_open)
            
            logger.info(f"Weather map saved to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating weather map: {e}")
            raise
    
    def run_demo(self, location: Tuple[float, float] = (40.7128, -74.0060),
                radius: int = 50) -> str:
        """
        Run a demo with sample data.
        
        Args:
            location: (latitude, longitude) for demo location
            radius: Search radius in kilometers
            
        Returns:
            Path to generated map file
        """
        logger.info(f"Running demo for location {location}")
        
        try:
            # Get weather data
            weather_data = self.get_weather_data(
                location[0], location[1], radius, include_forecast=True
            )
            
            # Create map
            output_file = f"demo_weather_map_{location[0]}_{location[1]}.html"
            map_path = self.create_weather_map(
                weather_data, 
                output_file=output_file,
                tile_layer='satellite'
            )
            
            logger.info(f"Demo completed. Map saved to {map_path}")
            return map_path
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise

def geocode_place(query: str) -> Tuple[float, float]:
    """Geocode a place name to (lat, lon) using Nominatim (OSM)."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "HyperlocalWeatherMap/1.0"}
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise ValueError(f"Location not found: {query}")
    return float(results[0]["lat"]), float(results[0]["lon"])


def main():
    """Main function to run the application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hyperlocal Weather Map')
    parser.add_argument('--lat', type=float, default=40.7128, help='Latitude')
    parser.add_argument('--lon', type=float, default=-74.0060, help='Longitude')
    parser.add_argument('--place', type=str, help='Place name to geocode (e.g., "Paris, France")')
    parser.add_argument('--interactive', action='store_true', help='Prompt for a place interactively')
    parser.add_argument('--radius', type=int, default=50, help='Search radius in km')
    parser.add_argument('--output', type=str, default='weather_map.html', help='Output file')
    parser.add_argument('--tile-layer', type=str, default='satellite', 
                       choices=['satellite', 'terrain', 'street'], help='Base tile layer')
    parser.add_argument('--no-open', action='store_true', help='Do not automatically open map in browser')
    
    args = parser.parse_args()
    
    try:
        # Resolve location
        if args.interactive and not args.place:
            args.place = input("Enter a place (e.g., 'Berlin, Germany' or '1600 Amphitheatre Pkwy, Mountain View'): ").strip()
        
        if args.place:
            lat, lon = geocode_place(args.place)
        else:
            lat, lon = args.lat, args.lon
        
        # Initialize app
        app = HyperlocalWeatherApp()
        
        # Get weather data
        weather_data = app.get_weather_data(lat, lon, args.radius)
        
        # Create map
        map_path = app.create_weather_map(
            weather_data, 
            output_file=args.output,
            tile_layer=args.tile_layer,
            auto_open=not args.no_open
        )
        
        print(f"✅ Weather map created successfully: {map_path}")
        if not args.no_open:
            print(f"🌐 Map should have opened automatically in your browser!")
        else:
            print(f"🌐 Open the file in your browser to view the interactive map")
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
