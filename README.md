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
