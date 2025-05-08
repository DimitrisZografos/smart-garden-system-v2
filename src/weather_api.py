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
            logger.warning("Weather API key is not set. Please add it to your config.yaml file.")
        
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
            logger.error(f"Unsupported weather provider: {self.provider}")
            raise ValueError(f"Unsupported weather provider: {self.provider}")
        
        self.last_update = time.time()
    
    def _update_openweathermap(self) -> None:
        """Update weather data from OpenWeatherMap API."""
        if not self.api_key:
            logger.error("OpenWeatherMap API key is not set. Please add it to your config.yaml file.")
            raise ValueError("Weather API key is required for fetching weather data")
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
            raise
    
    def _simulate_weather_data(self) -> None:
        """
        This method is deprecated and should not be used.
        
        Raises:
            RuntimeError: Always raised as real weather API is required
        """
        logger.error("Weather simulation is not available. Please provide a valid API key in config.yaml")
        raise RuntimeError("Weather API key is required for fetching weather data")