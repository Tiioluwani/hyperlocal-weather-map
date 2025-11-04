#!/usr/bin/env python3
"""
Quick start script for the hyperlocal weather map.
"""
import os
import sys
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import HyperlocalWeatherApp

def quick_start():
    """Quick start example."""
    print("🌤️ Hyperlocal Weather Map - Quick Start")
    print("=" * 45)
    
    # Check for API credentials
    client_id = os.getenv('XWEATHER_CLIENT_ID')
    client_secret = os.getenv('XWEATHER_CLIENT_SECRET')
    if not client_id or not client_secret:
        print("❌ Xweather API credentials not set!")
        print("   Please set your credentials:")
        print("   export XWEATHER_CLIENT_ID=your_client_id_here")
        print("   export XWEATHER_CLIENT_SECRET=your_client_secret_here")
        return 1
    
    try:
        # Initialize app
        print("🚀 Initializing weather app...")
        app = HyperlocalWeatherApp()
        
        # Use NYC as default location
        lat, lon = 40.7128, -74.0060
        print(f"📍 Location: New York City ({lat}, {lon})")
        
        # Get weather data
        print("🌤️ Fetching weather data...")
        weather_data = app.get_weather_data(lat, lon, radius=50)
        
        # Create map
        print("🗺️ Creating interactive map...")
        map_path = app.create_weather_map(
            weather_data,
            output_file='quick_start_map.html',
            tile_layer='satellite'
        )
        
        print(f"✅ Success! Map saved to: {map_path}")
        print("🌐 The map should have opened automatically in your browser!")
        print("   If not, manually open the HTML file in your browser.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(quick_start())
