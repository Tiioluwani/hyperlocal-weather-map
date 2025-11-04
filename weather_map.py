"""
Interactive weather map visualization using Xweather tiles and Folium.
"""
import folium
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Optional, Tuple
import json
import logging
import webbrowser
import os
from config import MAP_TILES_BASE_URL, XWEATHER_CLIENT_ID, XWEATHER_CLIENT_SECRET, DEFAULT_ZOOM, DEFAULT_CENTER
from folium.plugins import Geocoder, LocateControl, MousePosition
from folium import LatLngPopup

logger = logging.getLogger(__name__)

class WeatherMap:
    """
    Create interactive weather maps using Xweather tiles and weather data.
    """
    
    def __init__(self, center: Tuple[float, float] = None, zoom: int = None):
        """
        Initialize the weather map.
        
        Args:
            center: Map center coordinates (lat, lon)
            zoom: Initial zoom level
        """
        self.center = center or DEFAULT_CENTER
        self.zoom = zoom or DEFAULT_ZOOM
        
        # Xweather tile layers (credentials embedded in path)
        self.tile_layers = {
            "terrain":   f"{MAP_TILES_BASE_URL}/{XWEATHER_CLIENT_ID}_{XWEATHER_CLIENT_SECRET}/terrain/{{z}}/{{x}}/{{y}}.png",
            "satellite": f"{MAP_TILES_BASE_URL}/{XWEATHER_CLIENT_ID}_{XWEATHER_CLIENT_SECRET}/satellite/{{z}}/{{x}}/{{y}}.png",
            "street":    f"{MAP_TILES_BASE_URL}/{XWEATHER_CLIENT_ID}_{XWEATHER_CLIENT_SECRET}/street/{{z}}/{{x}}/{{y}}.png",
        }
        
        # Weather overlays (credentials embedded; current frame)
        self.weather_layers = {
            "radar":        f"{MAP_TILES_BASE_URL}/{XWEATHER_CLIENT_ID}_{XWEATHER_CLIENT_SECRET}/radar/{{z}}/{{x}}/{{y}}/current.png",
            "temperatures": f"{MAP_TILES_BASE_URL}/{XWEATHER_CLIENT_ID}_{XWEATHER_CLIENT_SECRET}/temperatures/{{z}}/{{x}}/{{y}}/current.png",
            "wind":         f"{MAP_TILES_BASE_URL}/{XWEATHER_CLIENT_ID}_{XWEATHER_CLIENT_SECRET}/wind/{{z}}/{{x}}/{{y}}/current.png",
        }
    
    def create_base_map(self, tile_layer: str = 'satellite') -> folium.Map:
        """
        Create a base map with Xweather tiles.
        
        Args:
            tile_layer: Base tile layer to use
            
        Returns:
            Folium map object
        """
        # Create base map
        m = folium.Map(
            location=self.center,
            zoom_start=self.zoom,
            tiles=None,  # We'll add custom tiles
            prefer_canvas=True
        )
        
        # Add basic interactivity controls
        Geocoder(add_marker=True, collapsed=True).add_to(m)
        LocateControl(auto_start=False, keepCurrentZoomLevel=True).add_to(m)
        MousePosition(position='bottomright', separator=' | ', empty_string='NaN',
                      lng_first=True, num_digits=6, prefix='Coords:').add_to(m)
        LatLngPopup().add_to(m)
        
        # Add Xweather base tile layer
        if tile_layer in self.tile_layers:
            folium.TileLayer(
                tiles=self.tile_layers[tile_layer],
                attr='Xweather',
                name=f'{tile_layer.title()} Base',
                overlay=False,
                control=True
            ).add_to(m)
        else:
            # Fallback to OpenStreetMap
            folium.TileLayer(
                tiles='OpenStreetMap',
                attr='OpenStreetMap contributors',
                name='OpenStreetMap',
                overlay=False,
                control=True
            ).add_to(m)
        
        return m
    
    def add_weather_observations(self, map_obj: folium.Map, 
                               observations: gpd.GeoDataFrame,
                               show_popup: bool = True) -> folium.Map:
        """
        Add weather observation markers to the map.
        
        Args:
            map_obj: Folium map object
            observations: GeoDataFrame with observation data
            show_popup: Whether to show popup information
            
        Returns:
            Updated map object
        """
        if observations.empty:
            return map_obj
        
        # Create feature group for observations
        obs_group = folium.FeatureGroup(name="Weather Observations")
        
        for idx, row in observations.iterrows():
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                continue
            
            # Determine marker color based on temperature
            temp = row.get('temperature', 0)
            if pd.isna(temp):
                color = 'gray'
            elif temp < 32:
                color = 'blue'
            elif temp < 50:
                color = 'lightblue'
            elif temp < 70:
                color = 'green'
            elif temp < 90:
                color = 'orange'
            else:
                color = 'red'
            
            # Create popup content
            popup_content = ""
            if show_popup:
                popup_content = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4>{row.get('name', 'Weather Station')}</h4>
                    <p><strong>Temperature:</strong> {temp:.1f}°F</p>
                    <p><strong>Humidity:</strong> {row.get('humidity', 'N/A')}%</p>
                    <p><strong>Pressure:</strong> {row.get('pressure', 'N/A')} inHg</p>
                    <p><strong>Wind:</strong> {row.get('wind_speed', 'N/A')} mph</p>
                    <p><strong>Weather:</strong> {row.get('weather', 'N/A')}</p>
                </div>
                """
            
            # Add marker
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                popup=folium.Popup(popup_content, max_width=250),
                color='white',
                weight=2,
                fillColor=color,
                fillOpacity=0.8,
                tooltip=f"Temp: {temp:.1f}°F"
            ).add_to(obs_group)
        
        obs_group.add_to(map_obj)
        return map_obj
    
    def add_weather_heatmap(self, map_obj: folium.Map, 
                          heatmap_data: List[Tuple[float, float, float]]) -> folium.Map:
        """
        Add temperature heatmap to the map.
        
        Args:
            map_obj: Folium map object
            heatmap_data: List of (lat, lon, value) tuples
            
        Returns:
            Updated map object
        """
        if not heatmap_data:
            return map_obj
        
        # Convert to the format expected by HeatMap
        heatmap_points = [[point[0], point[1], point[2]] for point in heatmap_data]
        
        # Add heatmap layer
        from folium.plugins import HeatMap
        
        heatmap_layer = HeatMap(
            heatmap_points,
            name="Temperature Heatmap",
            min_opacity=0.2,
            max_zoom=18,
            radius=25,
            blur=15,
            gradient={0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}
        )
        
        heatmap_layer.add_to(map_obj)
        return map_obj
    
    def add_weather_zones(self, map_obj: folium.Map, 
                         zones: gpd.GeoDataFrame) -> folium.Map:
        """
        Add weather zones to the map.
        
        Args:
            map_obj: Folium map object
            zones: GeoDataFrame with weather zone data
            
        Returns:
            Updated map object
        """
        if zones.empty:
            return map_obj
        
        # Create feature group for zones
        zones_group = folium.FeatureGroup(name="Weather Zones")
        
        for idx, row in zones.iterrows():
            # Determine zone color
            zone = row.get('zone', '')
            if 'Cold' in zone:
                color = 'blue'
            elif 'Moderate' in zone:
                color = 'green'
            elif 'Warm' in zone:
                color = 'red'
            else:
                color = 'gray'
            
            # Add zone marker
            folium.CircleMarker(
                location=[row['lat_mean'], row['lon_mean']],
                radius=15,
                popup=f"""
                <div style="font-family: Arial;">
                    <h4>{zone}</h4>
                    <p><strong>Stations:</strong> {row.get('station_count', 0)}</p>
                    <p><strong>Avg Temp:</strong> {row.get('temp_mean', 0):.1f}°F</p>
                    <p><strong>Humidity:</strong> {row.get('humidity_mean', 0):.1f}%</p>
                </div>
                """,
                color='white',
                weight=3,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(zones_group)
        
        zones_group.add_to(map_obj)
        return map_obj
    
    def add_weather_overlays(self, map_obj: folium.Map, 
                           overlay_types: List[str] = None) -> folium.Map:
        """
        Add Xweather weather overlay layers.
        """
        if overlay_types is None:
            overlay_types = ["radar", "temperatures", "wind"]
        
        for overlay_type in overlay_types:
            if overlay_type in self.weather_layers:
                folium.TileLayer(
                    tiles=self.weather_layers[overlay_type],
                    attr='Xweather',
                    name=f'{overlay_type.title()} Overlay',
                    overlay=True,
                    control=True,
                    opacity=0.6
                ).add_to(map_obj)
        
        return map_obj
    
    def add_forecast_markers(self, map_obj: folium.Map, 
                           forecast: gpd.GeoDataFrame) -> folium.Map:
        """
        Add forecast markers to the map.
        
        Args:
            map_obj: Folium map object
            forecast: GeoDataFrame with forecast data
            
        Returns:
            Updated map object
        """
        if forecast.empty:
            return map_obj
        
        # Create feature group for forecast
        forecast_group = folium.FeatureGroup(name="Weather Forecast")
        
        for idx, row in forecast.iterrows():
            # Create forecast popup
            popup_content = f"""
            <div style="font-family: Arial; width: 250px;">
                <h4>Forecast - {row.get('datetime', 'N/A')[:10]}</h4>
                <p><strong>High:</strong> {row.get('temperature_max', 'N/A')}°F</p>
                <p><strong>Low:</strong> {row.get('temperature_min', 'N/A')}°F</p>
                <p><strong>Humidity:</strong> {row.get('humidity', 'N/A')}%</p>
                <p><strong>Wind:</strong> {row.get('wind_speed', 'N/A')} mph</p>
                <p><strong>Weather:</strong> {row.get('weather', 'N/A')}</p>
            </div>
            """
            
            # Add forecast marker
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(
                    icon='cloud',
                    color='blue',
                    prefix='fa'
                ),
                tooltip="Forecast Data"
            ).add_to(forecast_group)
        
        forecast_group.add_to(map_obj)
        return map_obj
    
    def create_comprehensive_map(self, weather_data: Dict[str, gpd.GeoDataFrame],
                              tile_layer: str = 'satellite',
                              show_heatmap: bool = True,
                              show_zones: bool = True,
                              show_overlays: bool = True) -> folium.Map:
        """
        Create a comprehensive weather map with all available data.
        
        Args:
            weather_data: Dictionary with processed weather data
            tile_layer: Base tile layer to use
            show_heatmap: Whether to show temperature heatmap
            show_zones: Whether to show weather zones
            show_overlays: Whether to show weather overlays
            
        Returns:
            Complete weather map
        """
        # Create base map
        m = self.create_base_map(tile_layer)
        
        # Add observations
        if 'observations' in weather_data:
            m = self.add_weather_observations(m, weather_data['observations'])
        
        # Add heatmap
        if show_heatmap and 'observations' in weather_data:
            heatmap_data = self._create_heatmap_data(weather_data['observations'])
            m = self.add_weather_heatmap(m, heatmap_data)
        
        # Add weather zones
        if show_zones and 'weather_zones' in weather_data:
            m = self.add_weather_zones(m, weather_data['weather_zones'])
        
        # Add forecast
        if 'forecast' in weather_data:
            m = self.add_forecast_markers(m, weather_data['forecast'])
        
        # Add weather overlays
        if show_overlays:
            m = self.add_weather_overlays(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add legend
        self._add_legend(m)
        
        return m
    
    def _create_heatmap_data(self, observations: gpd.GeoDataFrame) -> List[Tuple[float, float, float]]:
        """Create heatmap data from observations."""
        if observations.empty:
            return []
        
        heatmap_data = []
        for idx, row in observations.iterrows():
            if not pd.isna(row.get('temperature')):
                heatmap_data.append((
                    row['latitude'],
                    row['longitude'],
                    row['temperature']
                ))
        
        return heatmap_data
    
    def _add_legend(self, map_obj: folium.Map):
        """Add a legend to the map."""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>Temperature Legend</h4>
        <p><span style="color:blue;">●</span> < 32°F (Freezing)</p>
        <p><span style="color:lightblue;">●</span> 32-50°F (Cold)</p>
        <p><span style="color:green;">●</span> 50-70°F (Cool)</p>
        <p><span style="color:orange;">●</span> 70-90°F (Warm)</p>
        <p><span style="color:red;">●</span> 90°F (Hot)</p>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    def save_map(self, map_obj: folium.Map, filename: str = 'weather_map.html', 
                 auto_open: bool = True):
        """
        Save the map to an HTML file and optionally open in browser.
        
        Args:
            map_obj: Folium map object
            filename: Output filename
            auto_open: Whether to automatically open in browser
        """
        map_obj.save(filename)
        logger.info(f"Map saved to {filename}")
        
        if auto_open:
            # Get the absolute path
            abs_path = os.path.abspath(filename)
            # Open in default browser
            webbrowser.open(f'file://{abs_path}')
            logger.info(f"Map opened in browser: {abs_path}")
