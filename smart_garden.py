"""
Smart Garden System - Main Application
Created by: Dimitris Zografos
Date: May 2025

This is the main application file for the Smart Garden System.
It integrates all components and provides the main control loop.
"""

import os
import time
import logging
import yaml
import json
import signal
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import our modules
from sensors import SensorManager
from actuators import ActuatorManager
from weather import WeatherManager
from notifications import NotificationManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('smart_garden.log')
    ]
)
logger = logging.getLogger('smart_garden')

class SmartGardenSystem:
    """
    Main class for the Smart Garden System.
    
    This class integrates all components and provides the main control loop.
    """
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize the Smart Garden System.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        self.system_config = self.config.get('system', {})
        self.check_interval = self.system_config.get('check_interval', 300)  # 5 minutes
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize components
        logger.info("Initializing Smart Garden System components...")
        self.sensor_manager = SensorManager(self.config)
        self.actuator_manager = ActuatorManager(self.config)
        self.weather_manager = WeatherManager(self.config)
        self.notification_manager = NotificationManager(self.config)
        
        # System state
        self.running = False
        self.last_watering_time = 0
        self.last_status_notification_time = 0
        
        logger.info("Smart Garden System initialized")
        
        # Send startup notification
        self.notification_manager.send_notification(
            "Smart Garden System started",
            'info'
        )
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dictionary containing configuration
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            # Return default configuration
            return {
                'system': {
                    'log_level': 'INFO',
                    'check_interval': 300
                }
            }
    
    def _signal_handler(self, sig, frame):
        """Handle signals for graceful shutdown."""
        logger.info(f"Received signal {sig}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the Smart Garden System main loop."""
        if self.running:
            logger.warning("Smart Garden System is already running")
            return
        
        self.running = True
        logger.info("Smart Garden System started")
        
        try:
            while self.running:
                self._run_cycle()
                
                # Sleep until next check
                logger.info(f"Sleeping for {self.check_interval} seconds until next check")
                time.sleep(self.check_interval)
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            self.notification_manager.notify_error(f"System error: {str(e)}")
            self.stop()
    
    def stop(self):
        """Stop the Smart Garden System."""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping Smart Garden System...")
        
        # Clean up resources
        try:
            self.sensor_manager.cleanup()
        except:
            pass
        
        try:
            self.actuator_manager.cleanup()
        except:
            pass
        
        # Send shutdown notification
        self.notification_manager.send_notification(
            "Smart Garden System stopped",
            'info'
        )
        
        logger.info("Smart Garden System stopped")
    
    def _run_cycle(self):
        """Run one cycle of the control loop."""
        logger.info("Starting control cycle")
        
        try:
            # Read sensor data
            logger.info("Reading sensors...")
            sensor_data = self.sensor_manager.read_all_sensors()
            
            # Get weather data
            logger.info("Getting weather data...")
            current_weather = self.weather_manager.get_current_weather()
            
            # Check if we should send a status notification
            current_time = time.time()
            status_interval = 6 * 3600  # 6 hours
            if current_time - self.last_status_notification_time > status_interval:
                logger.info("Sending status notification...")
                self.notification_manager.notify_system_status(sensor_data, current_weather)
                self.last_status_notification_time = current_time
            
            # Check soil moisture
            soil_moisture = sensor_data.get('soil_moisture', -1)
            if soil_moisture < 0:
                logger.error("Invalid soil moisture reading")
                self.notification_manager.notify_error("Invalid soil moisture reading")
                return
            
            # Check if soil moisture is low
            moisture_threshold = self.config.get('hardware', {}).get('soil_moisture', {}).get('threshold', 30)
            if soil_moisture < moisture_threshold:
                logger.info(f"Soil moisture ({soil_moisture}%) below threshold ({moisture_threshold}%)")
                
                # Check if we should water based on weather forecast
                skip_watering, reason = self.weather_manager.should_skip_watering()
                
                if skip_watering:
                    logger.info(f"Skipping watering: {reason}")
                    self.notification_manager.send_notification(
                        f"Watering skipped despite low moisture ({soil_moisture}%): {reason}",
                        'watering'
                    )
                else:
                    # Check if enough time has passed since last watering
                    min_watering_interval = 12 * 3600  # 12 hours
                    if current_time - self.last_watering_time > min_watering_interval:
                        # Water the plants
                        logger.info("Watering plants...")
                        watering_duration = self.config.get('hardware', {}).get('pump', {}).get('duration', 10)
                        success = self.actuator_manager.activate_pump(watering_duration)
                        
                        if success:
                            self.last_watering_time = current_time
                            self.notification_manager.notify_watering(soil_moisture, watering_duration)
                        else:
                            self.notification_manager.notify_error("Failed to activate water pump")
                    else:
                        hours_since_last = (current_time - self.last_watering_time) / 3600
                        logger.info(f"Skipping watering: Last watering was {hours_since_last:.1f} hours ago")
            else:
                logger.info(f"Soil moisture ({soil_moisture}%) above threshold ({moisture_threshold}%)")
            
            # Check temperature
            temperature = sensor_data.get('temperature', -999)
            if temperature > 35:  # High temperature threshold
                self.notification_manager.notify_high_temperature(temperature)
            
            logger.info("Control cycle completed")
            
        except Exception as e:
            logger.error(f"Error in control cycle: {str(e)}")
            self.notification_manager.notify_error(f"Control cycle error: {str(e)}")


# Main entry point
if __name__ == "__main__":
    print("Starting Smart Garden System...")
    print("Press Ctrl+C to stop")
    
    # Create and start the system
    system = SmartGardenSystem()
    system.start()