# Hyperlocal Weather Map with Xweather API

A comprehensive Python application for creating interactive hyperlocal weather maps using the Xweather API. This project demonstrates how to fetch, process, and visualize weather data with geospatial mapping capabilities.

## Features

- 🌤️ **Hyperlocal Weather Data**: Fetch real-time weather observations and forecasts
- 🗺️ **Interactive Maps**: Create beautiful maps with Xweather tiles and overlays
- 📊 **Data Processing**: Advanced geospatial data processing and analysis
- ⚡ **Performance Optimized**: Caching, rate limiting, and parallel processing
- 🎨 **Multiple Visualizations**: Heatmaps, weather zones, and forecast markers
- 🔧 **Easy to Use**: Simple API with comprehensive examples

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd hyperlocal-weather-map
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Xweather API credentials
XWEATHER_CLIENT_ID=your_client_id_here
XWEATHER_CLIENT_SECRET=your_client_secret_here
```

## Quick Start

### Basic Usage

```python
from main import HyperlocalWeatherApp

# Initialize the app
app = HyperlocalWeatherApp()

# Get weather data for New York City
weather_data = app.get_weather_data(40.7128, -74.0060, radius=50)

# Create an interactive map
map_path = app.create_weather_map(weather_data, 'nyc_weather.html')
print(f"Map saved to: {map_path}")
```

### Command Line Usage

```bash
# Run with default settings (NYC)
python main.py

# Run for a specific location
python main.py --lat 37.7749 --lon -122.4194 --radius 30

# Run demo mode
python main.py --demo

# Customize output and tile layer
python main.py --lat 40.7128 --lon -74.0060 --output my_map.html --tile-layer satellite
```

## API Reference

### HyperlocalWeatherApp

The main application class for weather mapping.

#### Methods

- `get_weather_data(center_lat, center_lon, radius=50, include_forecast=True)`
  - Fetch weather data for a location
  - Returns processed weather data dictionary

- `create_weather_map(weather_data, output_file='weather_map.html', tile_layer='satellite')`
  - Create interactive weather map
  - Returns path to saved HTML file

- `run_demo(location=(40.7128, -74.0060), radius=50)`
  - Run a complete demo with sample data

### XweatherClient

Client for interacting with the Xweather API.

#### Methods

- `get_observations(lat, lon, radius=50)`
  - Get current weather observations
  - Returns GeoDataFrame with observation data

- `get_forecast(lat, lon, days=5)`
  - Get weather forecast
  - Returns GeoDataFrame with forecast data

- `get_hyperlocal_data(center_lat, center_lon, radius=50, include_forecast=True)`
  - Get comprehensive weather data
  - Returns tuple of (observations, forecast)

### WeatherDataProcessor

Process and structure weather data for visualization.

#### Methods

- `clean_weather_data(df)`
  - Clean and validate weather data
  - Returns cleaned DataFrame

- `create_heatmap_data(df, lat_col='latitude', lon_col='longitude', value_col='temperature')`
  - Create heatmap data for visualization
  - Returns list of (lat, lon, value) tuples

- `aggregate_by_grid(df, grid_size=0.01)`
  - Aggregate weather data by grid cells
  - Returns GeoDataFrame with aggregated data

- `create_weather_zones(df, temp_threshold=5.0)`
  - Create weather zones based on temperature
  - Returns GeoDataFrame with weather zones

### WeatherMap

Create interactive weather maps with Xweather tiles.

#### Methods

- `create_base_map(tile_layer='satellite')`
  - Create base map with Xweather tiles
  - Returns Folium map object

- `add_weather_observations(map_obj, observations, show_popup=True)`
  - Add weather observation markers
  - Returns updated map object

- `add_weather_heatmap(map_obj, heatmap_data)`
  - Add temperature heatmap
  - Returns updated map object

- `add_weather_zones(map_obj, zones)`
  - Add weather zones
  - Returns updated map object

- `add_weather_overlays(map_obj, overlay_types=['radar', 'precipitation'])`
  - Add Xweather weather overlays
  - Returns updated map object

## Advanced Usage

### Custom Data Processing

```python
from data_processor import WeatherDataProcessor

processor = WeatherDataProcessor()

# Clean weather data
clean_data = processor.clean_weather_data(raw_observations)

# Create heatmap data
heatmap_data = processor.create_heatmap_data(clean_data)

# Aggregate by grid
grid_data = processor.aggregate_by_grid(clean_data, grid_size=0.01)

# Create weather zones
zones = processor.create_weather_zones(clean_data)
```

### Custom Map Creation

```python
from weather_map import WeatherMap

# Create custom map
map_builder = WeatherMap(center=(40.7128, -74.0060), zoom=12)

# Create base map
m = map_builder.create_base_map('satellite')

# Add custom layers
m = map_builder.add_weather_observations(m, observations)
m = map_builder.add_weather_heatmap(m, heatmap_data)
m = map_builder.add_weather_overlays(m, ['radar', 'precipitation'])

# Save map
map_builder.save_map(m, 'custom_map.html')
```

### Performance Optimization

```python
from optimization import PerformanceOptimizer, MapPerformanceOptimizer

# Initialize optimizers
perf_optimizer = PerformanceOptimizer()
map_optimizer = MapPerformanceOptimizer()

# Optimize API requests
optimized_requests = perf_optimizer.optimize_api_requests(requests_data)

# Optimize DataFrame operations
optimized_df = perf_optimizer.optimize_dataframe_operations(df)

# Optimize marker clustering
clustered_markers = map_optimizer.optimize_marker_clustering(df, cluster_threshold=50)
```

## Configuration

### Environment Variables

- `XWEATHER_CLIENT_ID`: Your Xweather client ID (required)
- `XWEATHER_CLIENT_SECRET`: Your Xweather client secret (required)
- `XWEATHER_BASE_URL`: Xweather API base URL (default: https://api.aerisapi.com)

### Config Settings

Edit `config.py` to customize:

- Cache settings (TTL, size)
- Map settings (default zoom, center)
- Weather data settings (radius, max points)

## Examples

### Example 1: Basic Weather Map

```python
from main import HyperlocalWeatherApp

app = HyperlocalWeatherApp()
weather_data = app.get_weather_data(40.7128, -74.0060, radius=50)
map_path = app.create_weather_map(weather_data, 'basic_map.html')
```

### Example 2: Custom Visualization

```python
from xweather_client import XweatherClient
from data_processor import WeatherDataProcessor
from weather_map import WeatherMap

# Get data
client = XweatherClient()
observations, forecast = client.get_hyperlocal_data(40.7128, -74.0060, 50)

# Process data
processor = WeatherDataProcessor()
processed_data = processor.prepare_for_mapping(observations, forecast)

# Create map
map_builder = WeatherMap()
m = map_builder.create_comprehensive_map(
    processed_data,
    tile_layer='terrain',
    show_heatmap=True,
    show_zones=True
)
map_builder.save_map(m, 'custom_visualization.html')
```

### Example 3: Performance Optimized

```python
from main import HyperlocalWeatherApp
from optimization import optimize_weather_app_performance

# Initialize app
app = HyperlocalWeatherApp()

# Apply performance optimizations
optimize_weather_app_performance(app)

# Run with optimizations
weather_data = app.get_weather_data(40.7128, -74.0060, radius=50)
map_path = app.create_weather_map(weather_data, 'optimized_map.html')
```

## Troubleshooting

### Common Issues

1. **API Credentials Error**: Make sure your Xweather client ID and client secret are set in the environment variables
2. **No Data Returned**: Check if the location has weather stations within the radius
3. **Map Not Loading**: Ensure all dependencies are installed and tile URLs are accessible
4. **Performance Issues**: Use the optimization utilities for large datasets

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Xweather for providing the weather API and map tiles
- Folium for interactive mapping capabilities
- GeoPandas for geospatial data processing
- The open-source community for various Python libraries
