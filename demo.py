"""
Comprehensive demo of the hyperlocal weather map application.
"""
import os
import sys
import logging
from main import HyperlocalWeatherApp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_comprehensive_demo():
    """Run a comprehensive demo of all features."""
    
    print("🌤️ Hyperlocal Weather Map Demo")
    print("=" * 50)
    
    try:
        # Initialize the app
        logger.info("Initializing Hyperlocal Weather App...")
        app = HyperlocalWeatherApp()
        
        # Demo locations
        demo_locations = [
            (40.7128, -74.0060, "New York City"),
            (34.0522, -118.2437, "Los Angeles"),
            (41.8781, -87.6298, "Chicago")
        ]
        
        for lat, lon, name in demo_locations:
            print(f"\n📍 Processing {name} ({lat}, {lon})")
            print("-" * 30)
            
            try:
                # Get weather data
                logger.info(f"Fetching weather data for {name}")
                weather_data = app.get_weather_data(lat, lon, radius=30, include_forecast=True)
                
                # Create map
                output_file = f"demo_{name.replace(' ', '_').lower()}_weather.html"
                map_path = app.create_weather_map(
                    weather_data,
                    output_file=output_file,
                    tile_layer='satellite'
                )
                
                print(f"✅ Map created: {map_path}")
                print(f"🌐 Map opened in browser: {map_path}")
                
                # Print data summary
                if 'observations' in weather_data and not weather_data['observations'].empty:
                    obs = weather_data['observations']
                    print(f"📊 Observations: {len(obs)} stations")
                    print(f"🌡️ Temperature range: {obs['temperature'].min():.1f}°F - {obs['temperature'].max():.1f}°F")
                    print(f"💧 Humidity range: {obs['humidity'].min():.1f}% - {obs['humidity'].max():.1f}%")
                
                if 'forecast' in weather_data and not weather_data['forecast'].empty:
                    forecast = weather_data['forecast']
                    print(f"🔮 Forecast periods: {len(forecast)}")
                
            except Exception as e:
                logger.error(f"Error processing {name}: {e}")
                print(f"❌ Failed to process {name}")
        
        print("\n🎉 Demo completed successfully!")
        print("\n📁 Generated files:")
        print("   - demo_new_york_city_weather.html")
        print("   - demo_los_angeles_weather.html") 
        print("   - demo_chicago_weather.html")
        print("\n🌐 Open any of these HTML files in your browser to view the interactive maps!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0

def main():
    """Main demo function."""
    print("🚀 Starting Hyperlocal Weather Map Demo...")
    print("This demo will create weather maps for multiple cities.")
    print("Make sure you have set your Xweather API credentials.")
    print()
    
    # Check for API credentials
    if not os.getenv('XWEATHER_CLIENT_ID') or not os.getenv('XWEATHER_CLIENT_SECRET'):
        print("⚠️  Warning: Xweather API credentials not found in environment variables.")
        print("   The demo will fail without proper credentials.")
        print("   Set your credentials:")
        print("   export XWEATHER_CLIENT_ID=your_client_id_here")
        print("   export XWEATHER_CLIENT_SECRET=your_client_secret_here")
        print()
    
    return run_comprehensive_demo()

if __name__ == "__main__":
    exit(main())
