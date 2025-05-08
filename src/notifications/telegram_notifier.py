"""
Telegram notification module for the Smart Garden System.
Sends alerts and status updates to a Telegram chat using a bot.
"""

import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """
    Handles sending notifications to Telegram.
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize the Telegram notifier.
        
        Args:
            bot_token: The Telegram bot token
            chat_id: The Telegram chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Validate configuration
        if not bot_token or not chat_id:
            logger.warning("Telegram notification configuration is incomplete. "
                          "Bot token and chat ID are required.")
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to the configured Telegram chat.
        
        Args:
            message: The message to send
            parse_mode: The parsing mode for the message (HTML or Markdown)
            
        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        if not self.bot_token or not self.chat_id:
            logger.warning("Cannot send Telegram notification: missing configuration")
            return False
            
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(self.api_url, data=payload)
            
            if response.status_code == 200:
                logger.debug(f"Telegram notification sent: {message[:50]}...")
                return True
            else:
                logger.error(f"Failed to send Telegram notification. "
                            f"Status code: {response.status_code}, "
                            f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.exception(f"Error sending Telegram notification: {str(e)}")
            return False
    
    def send_sensor_alert(self, sensor_type: str, value: float, 
                         threshold: float, unit: str = "") -> bool:
        """
        Send a sensor alert notification.
        
        Args:
            sensor_type: The type of sensor (e.g., "Soil Moisture", "Temperature")
            value: The current sensor value
            threshold: The threshold that was crossed
            unit: The unit of measurement (e.g., "%", "°C")
            
        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        message = (f"⚠️ <b>{sensor_type} Alert</b> ⚠️\n\n"
                  f"Current value: {value}{unit}\n"
                  f"Threshold: {threshold}{unit}")
        
        return self.send_message(message)
    
    def send_watering_notification(self, duration: int, 
                                  moisture_before: float) -> bool:
        """
        Send a notification that watering has started.
        
        Args:
            duration: The duration of watering in seconds
            moisture_before: The soil moisture percentage before watering
            
        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        message = (f"💧 <b>Watering Started</b> 💧\n\n"
                  f"Duration: {duration} seconds\n"
                  f"Soil moisture before: {moisture_before}%")
        
        return self.send_message(message)
    
    def send_system_status(self, status: Dict[str, Any]) -> bool:
        """
        Send a system status update.
        
        Args:
            status: A dictionary containing system status information
            
        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        # Format the status message
        message = "<b>🌱 Smart Garden System Status 🌱</b>\n\n"
        
        if "soil_moisture" in status:
            message += f"Soil Moisture: {status['soil_moisture']}%\n"
            
        if "temperature" in status:
            message += f"Temperature: {status['temperature']}°C\n"
            
        if "humidity" in status:
            message += f"Humidity: {status['humidity']}%\n"
            
        if "pressure" in status:
            message += f"Pressure: {status['pressure']} hPa\n"
            
        if "last_watered" in status:
            message += f"Last Watered: {status['last_watered']}\n"
            
        if "next_watering" in status:
            message += f"Next Watering: {status['next_watering']}\n"
            
        if "weather_forecast" in status:
            message += f"\n<b>Weather Forecast:</b>\n{status['weather_forecast']}\n"
        
        return self.send_message(message)
    
    def send_error_notification(self, error_message: str, 
                               component: Optional[str] = None) -> bool:
        """
        Send an error notification.
        
        Args:
            error_message: The error message
            component: The component that generated the error (optional)
            
        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        message = f"❌ <b>System Error</b> ❌\n\n"
        
        if component:
            message += f"Component: {component}\n"
            
        message += f"Error: {error_message}"
        
        return self.send_message(message)