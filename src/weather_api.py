"""
Weather API integration for the Smart Garden System.
"""

import logging
import requests
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WeatherAPI:
    """
    Interface for weather API services.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the weather API client.
        
        Args:
            config: Weather API configuration from config.yaml
        """
        self.config = config
        self.provider = config.get('provider', 'openweathermap')
        self.api_key = config.get('api_key', '')
        self.location = config.get('location', '')
        
        # Cache for weather data
        self.current_cache = {}
        self.forecast_cache = {}
        self.last_update = 0
        
        # Validate configuration
        if not self.api_key:
            logger.warning("Weather API key is not set. Weather data will be simulated.")
        
        if not self.location:
            logger.warning("Weather location is not set. Using default location.")
            self.location = "Volos,Greece"  # Default to Volos, Greece
        
        logger.info(f"Weather API initialized with provider: {self.provider}, location: {self.location}")
    
    def get_current(self) -> Dict[str, Any]:
        """
        Get current weather data.
        
        Returns:
            Dictionary with current weather data
        """
        # Check if we need to update the cache
        current_time = time.time()
        if (current_time - self.last_update > self.config.get('update_interval', 3600) or 
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
        if (current_time - self.last_update > self.config.get('update_interval', 3600) or 
            not self.forecast_cache):
            
            # Update the cache
            self._update_weather_data()
        
        return self.forecast_cache
    
    def _update_weather_data(self) -> None:
        """Update the weather data cache."""
        if self.provider == 'openweathermap':
            self._update_openweathermap()
        else:
            logger.warning(f"Unsupported weather provider: {self.provider}")
            self._simulate_weather_data()
        
        self.last_update = time.time()
    
    def _update_openweathermap(self) -> None:
        """Update weather data from OpenWeatherMap API."""
        if not self.api_key:
            logger.warning("OpenWeatherMap API key is not set. Using simulated data.")
            self._simulate_weather_data()
            return
        
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
                'icon': current_data['weather'][0]['icon'],
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
                        'description': item['weather'][0]['description'],
                        'icon': item['weather'][0]['icon']
                    }
                    for item in forecast_items
                ],
                'precipitation_probability': rain_probability
            }
            
            logger.info(f"Weather data updated for {self.location}")
            
        except Exception as e:
            logger.error(f"Error updating weather data: {str(e)}")
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
            'icon': '01d' if weather_type == 'Clear' else '03d' if weather_type == 'Clouds' else '10d',
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
                'description': f"{forecast_weather.lower()} sky",
                'icon': '01d' if forecast_weather == 'Clear' else '03d' if forecast_weather == 'Clouds' else '10d'
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