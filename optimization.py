"""
Optimization utilities for hyperlocal weather map performance.
"""
import time
import logging
from typing import Dict, List, Optional, Tuple
from cachetools import TTLCache
import requests
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """
    Performance optimization utilities for weather data processing.
    """
    
    def __init__(self, cache_size: int = 1000, cache_ttl: int = 300):
        """
        Initialize the performance optimizer.
        
        Args:
            cache_size: Maximum cache size
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        self.request_times = {}
        self.rate_limit_lock = threading.Lock()
        
    def optimize_api_requests(self, requests_data: List[Dict]) -> List[Dict]:
        """
        Optimize API requests by batching and deduplication.
        
        Args:
            requests_data: List of request parameters
            
        Returns:
            Optimized list of unique requests
        """
        # Remove duplicate requests
        unique_requests = []
        seen_requests = set()
        
        for req in requests_data:
            req_key = hash(frozenset(req.items()))
            if req_key not in seen_requests:
                unique_requests.append(req)
                seen_requests.add(req_key)
        
        logger.info(f"Optimized {len(requests_data)} requests to {len(unique_requests)} unique requests")
        return unique_requests
    
    def batch_requests(self, requests_data: List[Dict], 
                      batch_size: int = 10) -> List[List[Dict]]:
        """
        Split requests into batches for parallel processing.
        
        Args:
            requests_data: List of request parameters
            batch_size: Maximum batch size
            
        Returns:
            List of request batches
        """
        batches = []
        for i in range(0, len(requests_data), batch_size):
            batch = requests_data[i:i + batch_size]
            batches.append(batch)
        
        return batches
    
    def parallel_api_calls(self, requests_data: List[Dict], 
                          api_function, max_workers: int = 5) -> List:
        """
        Execute API calls in parallel.
        
        Args:
            requests_data: List of request parameters
            api_function: Function to call for each request
            max_workers: Maximum number of worker threads
            
        Returns:
            List of results
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_request = {
                executor.submit(api_function, req): req 
                for req in requests_data
            }
            
            # Collect results
            for future in as_completed(future_to_request):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"API call failed: {e}")
                    results.append(None)
        
        return results
    
    def optimize_dataframe_operations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize DataFrame operations for better performance.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Optimized DataFrame
        """
        if df.empty:
            return df
        
        # Convert object columns to category for memory efficiency
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # If less than 50% unique values
                df[col] = df[col].astype('category')
        
        # Optimize numeric columns
        for col in df.select_dtypes(include=['int64']).columns:
            if df[col].min() >= 0 and df[col].max() < 255:
                df[col] = df[col].astype('uint8')
            elif df[col].min() >= -128 and df[col].max() < 127:
                df[col] = df[col].astype('int8')
        
        return df
    
    def preload_tile_layers(self, map_obj, tile_layers: List[str]) -> None:
        """
        Preload tile layers for faster map rendering.
        
        Args:
            map_obj: Folium map object
            tile_layers: List of tile layer names to preload
        """
        for layer_name in tile_layers:
            # Add invisible tile layer to preload
            folium.TileLayer(
                tiles=f"https://maps.aerisapi.com/{layer_name}/{{z}}/{{x}}/{{y}}.png",
                attr='Xweather',
                name=f'Preload {layer_name}',
                overlay=True,
                control=False,
                opacity=0.01  # Nearly invisible
            ).add_to(map_obj)
    
    def implement_rate_limiting(self, max_requests_per_minute: int = 60) -> bool:
        """
        Implement rate limiting for API requests.
        
        Args:
            max_requests_per_minute: Maximum requests per minute
            
        Returns:
            True if request is allowed, False if rate limited
        """
        with self.rate_limit_lock:
            current_time = time.time()
            minute_ago = current_time - 60
            
            # Clean old requests
            self.request_times = {
                timestamp: count for timestamp, count in self.request_times.items()
                if timestamp > minute_ago
            }
            
            # Check if we're under the limit
            total_requests = sum(self.request_times.values())
            if total_requests >= max_requests_per_minute:
                logger.warning("Rate limit exceeded, waiting...")
                return False
            
            # Record this request
            current_minute = int(current_time // 60)
            self.request_times[current_minute] = self.request_times.get(current_minute, 0) + 1
            
            return True
    
    def optimize_memory_usage(self, data: Dict) -> Dict:
        """
        Optimize memory usage of weather data.
        
        Args:
            data: Dictionary with weather data
            
        Returns:
            Memory-optimized data
        """
        optimized_data = {}
        
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                optimized_data[key] = self.optimize_dataframe_operations(value)
            elif isinstance(value, gpd.GeoDataFrame):
                optimized_data[key] = self.optimize_dataframe_operations(value)
            else:
                optimized_data[key] = value
        
        return optimized_data
    
    def cache_weather_data(self, cache_key: str, data: Dict) -> None:
        """
        Cache weather data for faster subsequent access.
        
        Args:
            cache_key: Unique cache key
            data: Data to cache
        """
        self.cache[cache_key] = data
        logger.info(f"Cached data with key: {cache_key}")
    
    def get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """
        Retrieve cached weather data.
        
        Args:
            cache_key: Cache key to retrieve
            
        Returns:
            Cached data or None if not found
        """
        return self.cache.get(cache_key)
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        logger.info("Cache cleared")

class MapPerformanceOptimizer:
    """
    Optimize map rendering performance.
    """
    
    def __init__(self):
        """Initialize the map performance optimizer."""
        self.tile_cache = {}
        self.layer_cache = {}
    
    def optimize_marker_clustering(self, df: pd.DataFrame, 
                                  cluster_threshold: int = 50) -> List[Dict]:
        """
        Optimize marker display using clustering.
        
        Args:
            df: DataFrame with marker data
            cluster_threshold: Maximum markers per cluster
            
        Returns:
            List of clustered marker data
        """
        if len(df) <= cluster_threshold:
            return [{'lat': row['latitude'], 'lon': row['longitude'], 'data': row.to_dict()}
                   for _, row in df.iterrows()]
        
        # Simple grid-based clustering
        grid_size = 0.01  # degrees
        df['grid_lat'] = (df['latitude'] // grid_size) * grid_size
        df['grid_lon'] = (df['longitude'] // grid_size) * grid_size
        
        clusters = []
        for (grid_lat, grid_lon), group in df.groupby(['grid_lat', 'grid_lon']):
            if len(group) > cluster_threshold:
                # Create cluster
                cluster_data = {
                    'lat': grid_lat,
                    'lon': grid_lon,
                    'count': len(group),
                    'avg_temp': group['temperature'].mean() if 'temperature' in group.columns else None,
                    'is_cluster': True
                }
                clusters.append(cluster_data)
            else:
                # Add individual markers
                for _, row in group.iterrows():
                    clusters.append({
                        'lat': row['latitude'],
                        'lon': row['longitude'],
                        'data': row.to_dict(),
                        'is_cluster': False
                    })
        
        return clusters
    
    def optimize_heatmap_data(self, df: pd.DataFrame, 
                            max_points: int = 1000) -> List[Tuple[float, float, float]]:
        """
        Optimize heatmap data by sampling if too many points.
        
        Args:
            df: DataFrame with heatmap data
            max_points: Maximum number of points for heatmap
            
        Returns:
            Optimized heatmap data
        """
        if len(df) <= max_points:
            return [(row['latitude'], row['longitude'], row['temperature'])
                   for _, row in df.iterrows()]
        
        # Sample data if too many points
        sampled_df = df.sample(n=max_points, random_state=42)
        return [(row['latitude'], row['longitude'], row['temperature'])
               for _, row in sampled_df.iterrows()]
    
    def preload_map_tiles(self, map_bounds: Tuple[float, float, float, float],
                         zoom_levels: List[int] = [8, 9, 10, 11, 12]) -> None:
        """
        Preload map tiles for the given bounds and zoom levels.
        
        Args:
            map_bounds: (min_lat, min_lon, max_lat, max_lon)
            zoom_levels: List of zoom levels to preload
        """
        min_lat, min_lon, max_lat, max_lon = map_bounds
        
        for zoom in zoom_levels:
            # Calculate tile coordinates
            min_x = int((min_lon + 180) / 360 * (2 ** zoom))
            max_x = int((max_lon + 180) / 360 * (2 ** zoom))
            min_y = int((1 - np.log(np.tan(np.radians(max_lat)) + 1 / np.cos(np.radians(max_lat))) / np.pi) / 2 * (2 ** zoom))
            max_y = int((1 - np.log(np.tan(np.radians(min_lat)) + 1 / np.cos(np.radians(min_lat))) / np.pi) / 2 * (2 ** zoom))
            
            # Preload tiles
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    tile_key = f"{zoom}_{x}_{y}"
                    if tile_key not in self.tile_cache:
                        # Here you would implement actual tile preloading
                        self.tile_cache[tile_key] = True
        
        logger.info(f"Preloaded tiles for zoom levels: {zoom_levels}")

def optimize_weather_app_performance(app_instance) -> None:
    """
    Apply performance optimizations to the weather app.
    
    Args:
        app_instance: Instance of HyperlocalWeatherApp
    """
    # Add performance monitoring
    import time
    
    def timed_method(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
            return result
        return wrapper
    
    # Apply timing to key methods
    app_instance.get_weather_data = timed_method(app_instance.get_weather_data)
    app_instance.create_weather_map = timed_method(app_instance.create_weather_map)
    
    logger.info("Performance optimizations applied to weather app")
