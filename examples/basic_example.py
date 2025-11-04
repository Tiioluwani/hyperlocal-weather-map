"""
Basic example of using the hyperlocal weather map.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import HyperlocalWeatherApp
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run basic example."""
    try:
        # Initialize the app
        app = HyperlocalWeatherApp()
        
        # Define location (New York City)
        lat, lon = 40.7128, -74.0060
        radius = 50  # km
        
        logger.info(f"Fetching weather data for {lat}, {lon}")
        
        # Get weather data
        weather_data = app.get_weather_data(lat, lon, radius, include_forecast=True)
        
        # Create weather map
        map_path = app.create_weather_map(
            weather_data, 
            output_file='examples/basic_weather_map.html',
            tile_layer='satellite'
        )
        
        logger.info(f"✅ Weather map created: {map_path}")
        logger.info("🌐 Open the HTML file in your browser to view the interactive map")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
