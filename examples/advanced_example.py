"""
Advanced example demonstrating custom data processing and visualization.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xweather_client import XweatherClient
from data_processor import WeatherDataProcessor
from weather_map import WeatherMap
from optimization import PerformanceOptimizer, MapPerformanceOptimizer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run advanced example."""
    try:
        # Initialize components
        client = XweatherClient()
        processor = WeatherDataProcessor()
        map_builder = WeatherMap(center=(40.7128, -74.0060), zoom=10)
        perf_optimizer = PerformanceOptimizer()
        map_optimizer = MapPerformanceOptimizer()
        
        # Define multiple locations for comparison
        locations = [
            (40.7128, -74.0060, "New York City"),
            (34.0522, -118.2437, "Los Angeles"),
            (41.8781, -87.6298, "Chicago")
        ]
        
        all_observations = []
        
        # Fetch data for each location
        for lat, lon, name in locations:
            logger.info(f"Fetching data for {name}")
            
            # Get observations
            observations = client.get_observations(lat, lon, radius=30)
            if not observations.empty:
                observations['city'] = name
                all_observations.append(observations)
        
        # Combine all observations
        if all_observations:
            combined_obs = pd.concat(all_observations, ignore_index=True)
            
            # Process the data
            processed_data = processor.prepare_for_mapping(combined_obs)
            
            # Optimize performance
            optimized_data = perf_optimizer.optimize_memory_usage(processed_data)
            
            # Create comprehensive map
            m = map_builder.create_comprehensive_map(
                optimized_data,
                tile_layer='terrain',
                show_heatmap=True,
                show_zones=True,
                show_overlays=True
            )
            
            # Add custom features
            m = map_builder.add_weather_overlays(m, ['radar', 'precipitation', 'wind'])
            
            # Save map
            map_builder.save_map(m, 'examples/advanced_weather_map.html')
            
            logger.info("✅ Advanced weather map created: examples/advanced_weather_map.html")
            
            # Print statistics
            logger.info(f"📊 Total observations: {len(combined_obs)}")
            logger.info(f"🌡️ Temperature range: {combined_obs['temperature'].min():.1f}°F - {combined_obs['temperature'].max():.1f}°F")
            logger.info(f"🌍 Cities covered: {', '.join(combined_obs['city'].unique())}")
            
        else:
            logger.warning("No weather data retrieved")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import pandas as pd
    exit(main())
