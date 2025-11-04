"""
Performance optimization example.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import HyperlocalWeatherApp
from optimization import PerformanceOptimizer, MapPerformanceOptimizer, optimize_weather_app_performance
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def benchmark_performance():
    """Benchmark performance with and without optimizations."""
    
    # Test locations
    test_locations = [
        (40.7128, -74.0060, "New York City"),
        (34.0522, -118.2437, "Los Angeles"),
        (41.8781, -87.6298, "Chicago"),
        (29.7604, -95.3698, "Houston"),
        (33.4484, -112.0740, "Phoenix")
    ]
    
    # Initialize app
    app = HyperlocalWeatherApp()
    
    # Test without optimizations
    logger.info("🚀 Testing without optimizations...")
    start_time = time.time()
    
    for lat, lon, name in test_locations:
        try:
            weather_data = app.get_weather_data(lat, lon, radius=25)
            map_path = app.create_weather_map(
                weather_data, 
                f'examples/benchmark_{name.replace(" ", "_").lower()}_unoptimized.html'
            )
        except Exception as e:
            logger.warning(f"Failed for {name}: {e}")
    
    unoptimized_time = time.time() - start_time
    logger.info(f"⏱️ Unoptimized time: {unoptimized_time:.2f} seconds")
    
    # Apply optimizations
    optimize_weather_app_performance(app)
    
    # Test with optimizations
    logger.info("🚀 Testing with optimizations...")
    start_time = time.time()
    
    for lat, lon, name in test_locations:
        try:
            weather_data = app.get_weather_data(lat, lon, radius=25)
            map_path = app.create_weather_map(
                weather_data, 
                f'examples/benchmark_{name.replace(" ", "_").lower()}_optimized.html'
            )
        except Exception as e:
            logger.warning(f"Failed for {name}: {e}")
    
    optimized_time = time.time() - start_time
    logger.info(f"⏱️ Optimized time: {optimized_time:.2f} seconds")
    
    # Calculate improvement
    improvement = ((unoptimized_time - optimized_time) / unoptimized_time) * 100
    logger.info(f"📈 Performance improvement: {improvement:.1f}%")

def demonstrate_caching():
    """Demonstrate caching benefits."""
    logger.info("🗄️ Demonstrating caching benefits...")
    
    app = HyperlocalWeatherApp()
    lat, lon = 40.7128, -74.0060
    
    # First request (will be cached)
    start_time = time.time()
    weather_data1 = app.get_weather_data(lat, lon, radius=50)
    first_request_time = time.time() - start_time
    
    # Second request (should use cache)
    start_time = time.time()
    weather_data2 = app.get_weather_data(lat, lon, radius=50)
    second_request_time = time.time() - start_time
    
    logger.info(f"⏱️ First request: {first_request_time:.2f} seconds")
    logger.info(f"⏱️ Second request (cached): {second_request_time:.2f} seconds")
    logger.info(f"📈 Cache speedup: {first_request_time / second_request_time:.1f}x faster")

def demonstrate_parallel_processing():
    """Demonstrate parallel processing benefits."""
    logger.info("🔄 Demonstrating parallel processing...")
    
    from optimization import PerformanceOptimizer
    
    optimizer = PerformanceOptimizer()
    
    # Create sample requests
    requests_data = [
        {'lat': 40.7128, 'lon': -74.0060, 'radius': 25},
        {'lat': 34.0522, 'lon': -118.2437, 'radius': 25},
        {'lat': 41.8781, 'lon': -87.6298, 'radius': 25},
        {'lat': 29.7604, 'lon': -95.3698, 'radius': 25},
        {'lat': 33.4484, 'lon': -112.0740, 'radius': 25}
    ]
    
    # Optimize requests
    optimized_requests = optimizer.optimize_api_requests(requests_data)
    logger.info(f"📊 Optimized {len(requests_data)} requests to {len(optimized_requests)} unique requests")
    
    # Demonstrate batching
    batches = optimizer.batch_requests(optimized_requests, batch_size=2)
    logger.info(f"📦 Created {len(batches)} batches for parallel processing")

def main():
    """Run performance examples."""
    try:
        logger.info("🚀 Starting performance optimization examples...")
        
        # Benchmark performance
        benchmark_performance()
        
        # Demonstrate caching
        demonstrate_caching()
        
        # Demonstrate parallel processing
        demonstrate_parallel_processing()
        
        logger.info("✅ Performance examples completed!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
