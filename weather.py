"""
Smart Garden System - Weather API Module
Created by: Dimitris Zografos
Date: May 2025

This module handles weather API integration for the Smart Garden System.
It provides functions to fetch current weather and forecast data to help
make intelligent watering decisions.
"""

import time
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('weather')

# Try to import requests library
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("Requests library not available. Weather data will be simulated.")
    REQUESTS_AVAILABLE = False

class WeatherManager:
    """
    Manages weather data for the Smart Garden System.
    
    This class provides methods to fetch weather data from online APIs
    and use it to make intelligent watering decisions.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the weather manager with the provided configuration.
        
        Args:
            config: Dictionary containing weather configuration from config.yaml
        """
        self.config = config
        self.weather_config = config.get('weather', {})
        self.provider = self.weather_config.get('provider', 'openweathermap')
        self.api_key = self.weather_config.get('api_key', '')
        self.location = self.weather_config.get('location', 'Volos,Greece')
        self.update_interval = self.weather_config.get('update_interval', 3600)  # 1 hour
        
        # Cache for weather data
        self.current_cache = {}
        self.forecast_cache = {}
        self.last_update = 0
        
        # Storage path for weather data
        self.storage_path = config.get('data', {}).get('storage_path', './data')
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        
        # Validate configuration
        if not self.api_key and REQUESTS_AVAILABLE:
            logger.warning("Weather API key is not set. Please add it to your config.yaml file.")
        
        logger.info(f"Weather manager initialized for location: {self.location}")
    
    def get_current_weather(self) -> Dict[str, Any]:
        """
        Get current weather data.
        
        Returns:
            Dictionary with current weather data
        """
        # Check if we need to update the cache
        current_time = time.time()
        if (current_time - self.last_update > self.update_interval or 
            not self.current_cache):
            
            # Update the cache
            self._update_weather_data()
        
        return self.current_cache
    
    def get_forecast(self) -> Dict[str, Any]:
        """
        Get weather forecast data.
        
        Returns:
            Dictionary with forecast weather data
        """
        # Check if we need to update the cache
        current_time = time.time()
        if (current_time - self.last_update > self.update_interval or 
            not self.forecast_cache):
            
            # Update the cache
            self._update_weather_data()
        
        return self.forecast_cache
    
    def _update_weather_data(self) -> None:
        """Update the weather data cache."""
        if not REQUESTS_AVAILABLE or not self.api_key:
            # Use simulated data if requests is not available or API key is not set
            self._simulate_weather_data()
            return
        
        if self.provider == 'openweathermap':
            self._update_openweathermap()
        else:
            logger.error(f"Unsupported weather provider: {self.provider}")
            self._simulate_weather_data()
        
        self.last_update = time.time()
        
        # Save weather data to file
        self._save_weather_data()
    
    def _update_openweathermap(self) -> None:
        """Update weather data from OpenWeatherMap API."""
        try:
            # Get current weather
            current_url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={self.location}&appid={self.api_key}&units=metric"
            )
            
            current_response = requests.get(current_url)
            current_response.raise_for_status()
            current_data = current_response.json()
            
            # Process current weather data
            self.current_cache = {
                'temperature': current_data['main']['temp'],
                'humidity': current_data['main']['humidity'],
                'pressure': current_data['main']['pressure'],
                'wind_speed': current_data['wind']['speed'],
                'weather': current_data['weather'][0]['main'],
                'description': current_data['weather'][0]['description'],
                'precipitation_probability': 0,  # Not available in current weather
                'timestamp': current_data['dt']
            }
            
            # Get forecast
            forecast_url = (
                f"https://api.openweathermap.org/data/2.5/forecast"
                f"?q={self.location}&appid={self.api_key}&units=metric"
            )
            
            forecast_response = requests.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            # Process forecast data
            forecast_items = forecast_data['list'][:8]  # Next 24 hours (3-hour intervals)
            
            # Check for rain in the forecast
            rain_probability = 0
            for item in forecast_items:
                if 'rain' in item:
                    rain_probability = max(rain_probability, 80)  # Approximate
                elif item['weather'][0]['main'] in ['Rain', 'Drizzle', 'Thunderstorm']:
                    rain_probability = max(rain_probability, 70)  # Approximate
            
            # Create a summary
            weather_types = set(item['weather'][0]['main'] for item in forecast_items)
            temp_min = min(item['main']['temp'] for item in forecast_items)
            temp_max = max(item['main']['temp'] for item in forecast_items)
            
            summary = (
                f"Next 24 hours: {', '.join(weather_types)}. "
                f"Temperatures between {temp_min:.1f}°C and {temp_max:.1f}°C. "
            )
            
            if rain_probability > 50:
                summary += "Rain is expected."
            
            self.forecast_cache = {
                'summary': summary,
                'items': [
                    {
                        'timestamp': item['dt'],
                        'temperature': item['main']['temp'],
                        'weather': item['weather'][0]['main'],
                        'description': item['weather'][0]['description']
                    }
                    for item in forecast_items
                ],
                'precipitation_probability': rain_probability
            }
            
            logger.info(f"Weather data updated for {self.location}")
            
        except Exception as e:
            logger.error(f"Error updating weather data: {str(e)}")
            # Fall back to simulated data
            self._simulate_weather_data()
    
    def _simulate_weather_data(self) -> None:
        """Generate simulated weather data."""
        import random
        from datetime import datetime, timedelta
        
        # Simulate current weather
        temperature = random.uniform(15.0, 30.0)
        weather_types = ['Clear', 'Clouds', 'Rain']
        weather_type = random.choice(weather_types)
        
        self.current_cache = {
            'temperature': round(temperature, 1),
            'humidity': round(random.uniform(40.0, 80.0), 1),
            'pressure': round(random.uniform(1000.0, 1020.0), 1),
            'wind_speed': round(random.uniform(0.0, 10.0), 1),
            'weather': weather_type,
            'description': f"{weather_type.lower()} sky",
            'precipitation_probability': 80 if weather_type == 'Rain' else 20 if weather_type == 'Clouds' else 0,
            'timestamp': int(time.time())
        }
        
        # Simulate forecast
        now = datetime.now()
        forecast_items = []
        
        for i in range(8):
            forecast_time = now + timedelta(hours=i*3)
            forecast_temp = temperature + random.uniform(-5.0, 5.0)
            forecast_weather = random.choice(weather_types)
            
            forecast_items.append({
                'timestamp': int(forecast_time.timestamp()),
                'temperature': round(forecast_temp, 1),
                'weather': forecast_weather,
                'description': f"{forecast_weather.lower()} sky"
            })
        
        # Create a summary
        weather_types = set(item['weather'] for item in forecast_items)
        temp_min = min(item['temperature'] for item in forecast_items)
        temp_max = max(item['temperature'] for item in forecast_items)
        
        rain_probability = 80 if 'Rain' in weather_types else 20 if 'Clouds' in weather_types else 0
        
        summary = (
            f"Next 24 hours: {', '.join(weather_types)}. "
            f"Temperatures between {temp_min:.1f}°C and {temp_max:.1f}°C. "
        )
        
        if rain_probability > 50:
            summary += "Rain is expected."
        
        self.forecast_cache = {
            'summary': summary,
            'items': forecast_items,
            'precipitation_probability': rain_probability
        }
        
        logger.info("Simulated weather data generated")
    
    def _save_weather_data(self) -> None:
        """Save weather data to a JSON file."""
        try:
            # Create filename based on date
            date_str = datetime.now().strftime('%Y%m%d')
            filename = os.path.join(self.storage_path, f"weather_data_{date_str}.json")
            
            # Combine current and forecast data
            data = {
                'timestamp': datetime.now().isoformat(),
                'location': self.location,
                'current': self.current_cache,
                'forecast': self.forecast_cache
            }
            
            # Save data
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved weather data to {filename}")
        except Exception as e:
            logger.error(f"Error saving weather data: {str(e)}")
    
    def should_skip_watering(self) -> Tuple[bool, str]:
        """
        Determine if watering should be skipped based on weather forecast.
        
        Returns:
            Tuple of (should_skip, reason)
        """
        # Get forecast data
        forecast = self.get_forecast()
        
        # Check if rain is expected
        rain_probability = forecast.get('precipitation_probability', 0)
        if rain_probability > 50:
            return True, f"Rain is expected (probability: {rain_probability}%)"
        
        # Check current temperature
        current = self.get_current_weather()
        temperature = current.get('temperature', 20)
        if temperature < 5:
            return True, f"Temperature too low ({temperature}°C)"
        
        # No reason to skip watering
        return False, ""


# Example usage if this file is run directly
if __name__ == "__main__":
    import yaml
    from typing import Tuple
    
    # Load configuration
    try:
        with open("config/config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        config = {}
    
    # Create weather manager
    weather_manager = WeatherManager(config)
    
    # Get current weather
    print("Getting current weather...")
    current = weather_manager.get_current_weather()
    
    # Print current weather
    print("\nCurrent Weather:")
    print(f"Temperature: {current['temperature']}°C")
    print(f"Humidity: {current['humidity']}%")
    print(f"Pressure: {current['pressure']} hPa")
    print(f"Wind Speed: {current['wind_speed']} m/s")
    print(f"Weather: {current['weather']} ({current['description']})")
    
    # Get forecast
    print("\nGetting forecast...")
    forecast = weather_manager.get_forecast()
    
    # Print forecast summary
    print("\nForecast Summary:")
    print(forecast['summary'])
    
    # Check if watering should be skipped
    skip_watering, reason = weather_manager.should_skip_watering()
    print("\nWatering Decision:")
    if skip_watering:
        print(f"Watering should be skipped: {reason}")
    else:
        print("Watering can proceed as scheduled")