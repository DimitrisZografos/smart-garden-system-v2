"""
Smart Garden System - Notification Module
Created by: Dimitris Zografos
Date: May 2025

This module handles notifications for the Smart Garden System.
It provides functions to send alerts via Telegram.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('notifications')

# Try to import telegram library
try:
    import telegram
    TELEGRAM_AVAILABLE = True
except ImportError:
    logger.warning("Telegram library not available. Notifications will be logged only.")
    TELEGRAM_AVAILABLE = False

class NotificationManager:
    """
    Manages notifications for the Smart Garden System.
    
    This class provides methods to send notifications about system events,
    such as watering events, sensor readings, and errors.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the notification manager with the provided configuration.
        
        Args:
            config: Dictionary containing notification configuration from config.yaml
        """
        self.config = config
        self.notification_config = config.get('notifications', {})
        self.telegram_config = self.notification_config.get('telegram', {})
        self.enabled = self.telegram_config.get('enabled', False)
        self.token = self.telegram_config.get('token', '')
        self.chat_id = self.telegram_config.get('chat_id', '')
        self.notify_on = self.telegram_config.get('notify_on', {})
        
        # Initialize Telegram bot if enabled and available
        self.bot = None
        if self.enabled and TELEGRAM_AVAILABLE and self.token and self.chat_id:
            try:
                self.bot = telegram.Bot(token=self.token)
                logger.info("Telegram bot initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {str(e)}")
                self.bot = None
        elif self.enabled:
            if not TELEGRAM_AVAILABLE:
                logger.warning("Telegram notifications enabled but library not available")
            elif not self.token:
                logger.warning("Telegram notifications enabled but token not set")
            elif not self.chat_id:
                logger.warning("Telegram notifications enabled but chat_id not set")
    
    def send_notification(self, message: str, category: str = 'info', image_path: Optional[str] = None) -> bool:
        """
        Send a notification.
        
        Args:
            message: The message to send
            category: The category of the notification (info, watering, low_moisture, high_temperature, error)
            image_path: Optional path to an image to include with the notification
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        # Check if notifications are enabled for this category
        if category != 'info' and not self.notify_on.get(category, True):
            logger.debug(f"Notifications for category '{category}' are disabled")
            return False
        
        # Always log the notification
        log_level = logging.ERROR if category == 'error' else logging.INFO
        logger.log(log_level, f"NOTIFICATION ({category}): {message}")
        
        # Send via Telegram if available
        if self.bot is not None:
            try:
                # Add timestamp to message
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                full_message = f"[{timestamp}] {message}"
                
                # Send message
                if image_path and image_path != "":
                    # Send image with caption
                    self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=open(image_path, 'rb'),
                        caption=full_message
                    )
                else:
                    # Send text message
                    self.bot.send_message(
                        chat_id=self.chat_id,
                        text=full_message
                    )
                
                logger.debug(f"Telegram notification sent: {message}")
                return True
            except Exception as e:
                logger.error(f"Failed to send Telegram notification: {str(e)}")
                return False
        
        return False
    
    def notify_watering(self, soil_moisture: int, duration: int) -> bool:
        """
        Send a notification about a watering event.
        
        Args:
            soil_moisture: The soil moisture percentage that triggered watering
            duration: The duration of the watering in seconds
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        message = f"Plants watered for {duration} seconds (soil moisture: {soil_moisture}%)"
        return self.send_notification(message, 'watering')
    
    def notify_low_moisture(self, soil_moisture: int) -> bool:
        """
        Send a notification about low soil moisture.
        
        Args:
            soil_moisture: The current soil moisture percentage
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        message = f"Low soil moisture detected: {soil_moisture}%"
        return self.send_notification(message, 'low_moisture')
    
    def notify_high_temperature(self, temperature: float) -> bool:
        """
        Send a notification about high temperature.
        
        Args:
            temperature: The current temperature in °C
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        message = f"High temperature detected: {temperature}°C"
        return self.send_notification(message, 'high_temperature')
    
    def notify_error(self, error_message: str) -> bool:
        """
        Send a notification about an error.
        
        Args:
            error_message: The error message
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        message = f"ERROR: {error_message}"
        return self.send_notification(message, 'error')
    
    def notify_system_status(self, sensor_data: Dict[str, Any], weather_data: Dict[str, Any]) -> bool:
        """
        Send a notification with the current system status.
        
        Args:
            sensor_data: Dictionary containing sensor readings
            weather_data: Dictionary containing weather data
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        # Create status message
        message = "Smart Garden System Status\n\n"
        
        # Add sensor data
        message += "Sensor Readings:\n"
        message += f"- Soil Moisture: {sensor_data.get('soil_moisture', 'N/A')}%\n"
        message += f"- Temperature: {sensor_data.get('temperature', 'N/A')}°C\n"
        message += f"- Humidity: {sensor_data.get('humidity', 'N/A')}%\n"
        message += f"- Pressure: {sensor_data.get('pressure', 'N/A')} hPa\n\n"
        
        # Add weather data
        message += "Weather:\n"
        message += f"- Current: {weather_data.get('weather', 'N/A')} ({weather_data.get('description', 'N/A')})\n"
        message += f"- Temperature: {weather_data.get('temperature', 'N/A')}°C\n"
        
        # Add forecast if available
        forecast = weather_data.get('forecast', {})
        if forecast:
            message += f"\nForecast: {forecast.get('summary', 'N/A')}\n"
        
        # Send notification with image if available
        image_path = sensor_data.get('image_path', '')
        return self.send_notification(message, 'info', image_path)


# Example usage if this file is run directly
if __name__ == "__main__":
    import yaml
    
    # Load configuration
    try:
        with open("config/config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        config = {}
    
    # Create notification manager
    notification_manager = NotificationManager(config)
    
    # Test notifications
    print("Testing notifications...")
    
    # Test info notification
    notification_manager.send_notification("This is a test notification", 'info')
    
    # Test watering notification
    notification_manager.notify_watering(25, 10)
    
    # Test low moisture notification
    notification_manager.notify_low_moisture(15)
    
    # Test high temperature notification
    notification_manager.notify_high_temperature(35.5)
    
    # Test error notification
    notification_manager.notify_error("This is a test error message")
    
    # Test system status notification
    sensor_data = {
        'soil_moisture': 30,
        'temperature': 25.5,
        'humidity': 60.0,
        'pressure': 1013.2,
        'image_path': ''  # No image for this test
    }
    
    weather_data = {
        'temperature': 26.0,
        'weather': 'Clear',
        'description': 'clear sky',
        'forecast': {
            'summary': 'Next 24 hours: Clear, Clouds. Temperatures between 20.5°C and 28.5°C.'
        }
    }
    
    notification_manager.notify_system_status(sensor_data, weather_data)