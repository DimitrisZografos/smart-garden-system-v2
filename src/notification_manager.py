"""
Notification manager for the Smart Garden System.
Handles sending notifications through configured channels.
"""

import logging
from typing import Dict, Any, Optional
from .notifications.telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Manages notifications for the Smart Garden System.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the notification manager.
        
        Args:
            config: The notification configuration from config.yaml
        """
        self.config = config
        self.telegram = None
        
        # Initialize notification channels
        self._init_telegram()
        
        logger.info("Notification manager initialized")
    
    def _init_telegram(self) -> None:
        """Initialize the Telegram notifier if enabled."""
        if self.config.get('telegram', {}).get('enabled', False):
            bot_token = self.config.get('telegram', {}).get('bot_token', '')
            chat_id = self.config.get('telegram', {}).get('chat_id', '')
            
            if bot_token and chat_id:
                self.telegram = TelegramNotifier(bot_token, chat_id)
                logger.info("Telegram notifications enabled")
            else:
                logger.warning("Telegram notifications enabled but missing bot_token or chat_id")
    
    def send_sensor_alert(self, sensor_type: str, value: float, 
                         threshold: float, unit: str = "") -> None:
        """
        Send a sensor alert notification.
        
        Args:
            sensor_type: The type of sensor (e.g., "Soil Moisture", "Temperature")
            value: The current sensor value
            threshold: The threshold that was crossed
            unit: The unit of measurement (e.g., "%", "°C")
        """
        logger.info(f"Sending {sensor_type} alert: {value}{unit} (threshold: {threshold}{unit})")
        
        # Send via Telegram
        if self.telegram:
            self.telegram.send_sensor_alert(sensor_type, value, threshold, unit)
    
    def send_watering_notification(self, duration: int, 
                                  moisture_before: float) -> None:
        """
        Send a notification that watering has started.
        
        Args:
            duration: The duration of watering in seconds
            moisture_before: The soil moisture percentage before watering
        """
        logger.info(f"Sending watering notification: {duration}s, moisture: {moisture_before}%")
        
        # Send via Telegram
        if self.telegram:
            self.telegram.send_watering_notification(duration, moisture_before)
    
    def send_system_status(self, status: Dict[str, Any]) -> None:
        """
        Send a system status update.
        
        Args:
            status: A dictionary containing system status information
        """
        logger.debug("Sending system status notification")
        
        # Send via Telegram
        if self.telegram:
            self.telegram.send_system_status(status)
    
    def send_error_notification(self, error_message: str, 
                               component: Optional[str] = None) -> None:
        """
        Send an error notification.
        
        Args:
            error_message: The error message
            component: The component that generated the error (optional)
        """
        logger.error(f"System error in {component or 'unknown'}: {error_message}")
        
        # Send via Telegram
        if self.telegram:
            self.telegram.send_error_notification(error_message, component)