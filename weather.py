#!/usr/bin/env python3
"""
Smart Garden System - Weather Module
This module handles weather forecast retrieval for the Smart Garden System.
It provides a unified interface for getting weather forecasts from OpenWeatherMap.

If the API key is not provided or invalid, it will return simulated weather data.
"""

import requests
import json
import random
import logging
import time
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('weather')

class WeatherForecast:
    """Retrieves and processes weather forecast data"""
    
    def __init__(self, api_key=None, location="London"):
        """
        Initialize the weather forecast module
        
        Args:
            api_key (str): OpenWeatherMap API key
            location (str): Location for weather forecast
        """
        self.api_key = api_key
        self.location = location
        self.last_forecast = None
        self.last_update = None
        self.update_interval = 3600  # Update every hour
        
        logger.info(f"Initializing WeatherForecast for {location}")
        
        # Test API key if provided
        if api_key:
            self.test_api_key()
    
    def test_api_key(self):
        """Test if the API key is valid"""
        if not self.api_key:
            logger.warning("No API key provided")
            return False
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={self.location}&appid={self.api_key}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("API key is valid")
                return True
            else:
                logger.warning(f"API key test failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error testing API key: {e}")
            return False
    
    def get_forecast(self, force_update=False):
        """
        Get the weather forecast
        
        Args:
            force_update (bool): If True, force an update regardless of the update interval
            
        Returns:
            str: Weather forecast summary
        """
        # Check if we need to update the forecast
        current_time = time.time()
        if (self.last_update is None or 
            current_time - self.last_update > self.update_interval or
            force_update):
            
            # Try to get real forecast if API key is provided
            if self.api_key:
                try:
                    forecast = self._get_real_forecast()
                    if forecast:
                        self.last_forecast = forecast
                        self.last_update = current_time
                        return forecast
                except Exception as e:
                    logger.error(f"Error getting real forecast: {e}")
            
            # Fall back to simulated forecast
            forecast = self._get_simulated_forecast()
            self.last_forecast = forecast
            self.last_update = current_time
            return forecast
        
        # Return cached forecast
        return self.last_forecast
    
    def _get_real_forecast(self):
        """
        Get the real weather forecast from OpenWeatherMap
        
        Returns:
            str: Weather forecast summary
        """
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={self.location}&appid={self.api_key}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Failed to get forecast: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        
        # Process forecast data
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Get today's forecast
        today_forecasts = [item for item in data['list'] if datetime.fromtimestamp(item['dt']).date() == today]
        today_temps = [item['main']['temp'] for item in today_forecasts]
        today_conditions = [item['weather'][0]['main'] for item in today_forecasts]
        
        # Get tomorrow's forecast
        tomorrow_forecasts = [item for item in data['list'] if datetime.fromtimestamp(item['dt']).date() == tomorrow]
        tomorrow_temps = [item['main']['temp'] for item in tomorrow_forecasts]
        tomorrow_conditions = [item['weather'][0]['main'] for item in tomorrow_forecasts]
        
        # Create forecast summary
        if today_forecasts and tomorrow_forecasts:
            today_max = max(today_temps)
            today_min = min(today_temps)
            today_condition = max(set(today_conditions), key=today_conditions.count)
            
            tomorrow_max = max(tomorrow_temps)
            tomorrow_min = min(tomorrow_temps)
            tomorrow_condition = max(set(tomorrow_conditions), key=tomorrow_conditions.count)
            
            rain_chance = "low"
            if "Rain" in today_conditions or "Rain" in tomorrow_conditions:
                rain_chance = "high"
            elif "Clouds" in today_conditions or "Clouds" in tomorrow_conditions:
                rain_chance = "medium"
            
            forecast = (
                f"Today in {self.location}: {today_condition}, {today_min:.1f}°C to {today_max:.1f}°C. "
                f"Tomorrow: {tomorrow_condition}, {tomorrow_min:.1f}°C to {tomorrow_max:.1f}°C. "
                f"Chance of rain: {rain_chance}."
            )
            
            logger.info(f"Retrieved forecast: {forecast}")
            return forecast
        
        return None
    
    def _get_simulated_forecast(self):
        """
        Get a simulated weather forecast
        
        Returns:
            str: Simulated weather forecast summary
        """
        # Generate random weather data
        conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Rain", "Thunderstorm"]
        today_condition = random.choice(conditions)
        tomorrow_condition = random.choice(conditions)
        
        today_max = random.uniform(15, 30)
        today_min = today_max - random.uniform(5, 10)
        
        tomorrow_max = today_max + random.uniform(-5, 5)
        tomorrow_min = tomorrow_max - random.uniform(5, 10)
        
        rain_chance = "low"
        if "Rain" in today_condition or "Rain" in tomorrow_condition or "Thunderstorm" in today_condition or "Thunderstorm" in tomorrow_condition:
            rain_chance = "high"
        elif "Cloudy" in today_condition or "Cloudy" in tomorrow_condition:
            rain_chance = "medium"
        
        forecast = (
            f"[SIMULATED] Today in {self.location}: {today_condition}, {today_min:.1f}°C to {today_max:.1f}°C. "
            f"Tomorrow: {tomorrow_condition}, {tomorrow_min:.1f}°C to {tomorrow_max:.1f}°C. "
            f"Chance of rain: {rain_chance}."
        )
        
        logger.info(f"Generated simulated forecast: {forecast}")
        print(f"[SIMULATION] Weather forecast: {forecast}")
        return forecast

if __name__ == "__main__":
    # Simple test code
    weather = WeatherForecast()  # No API key, will use simulation
    
    print("Testing weather forecast...")
    forecast = weather.get_forecast()
    print(forecast)
    
    # Test with invalid API key
    weather = WeatherForecast(api_key="invalid_key")
    forecast = weather.get_forecast()
    print(forecast)