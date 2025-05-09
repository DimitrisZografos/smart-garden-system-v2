"""
Smart Garden System - Hardware Test Script
Created by: Dimitris Zografos
Date: May 2025

This script tests all hardware components of the Smart Garden System.
Run this script to verify that all sensors and actuators are working properly.
"""

import time
import logging
import yaml
import os
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('hardware_test')

def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        config_path = 'config/config.yaml'
        if not os.path.exists(config_path):
            logger.warning(f"Configuration file not found at {config_path}")
            logger.info("Using example configuration file")
            config_path = 'config/config.yaml.example'
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return {}

def test_soil_moisture_sensor(config: Dict[str, Any]) -> bool:
    """Test the soil moisture sensor."""
    from sensors import SensorManager
    
    logger.info("Testing soil moisture sensor...")
    
    try:
        # Create sensor manager
        sensor_manager = SensorManager(config)
        
        # Read soil moisture
        moisture = sensor_manager.read_soil_moisture()
        
        if moisture < 0:
            logger.error("Failed to read soil moisture")
            return False
        
        logger.info(f"Soil moisture reading: {moisture}%")
        
        # Clean up
        sensor_manager.cleanup()
        
        return True
    except Exception as e:
        logger.error(f"Error testing soil moisture sensor: {str(e)}")
        return False

def test_bme280_sensor(config: Dict[str, Any]) -> bool:
    """Test the BME280 temperature/humidity/pressure sensor."""
    from sensors import SensorManager
    
    logger.info("Testing BME280 sensor...")
    
    try:
        # Create sensor manager
        sensor_manager = SensorManager(config)
        
        # Read temperature, humidity, pressure
        temperature, humidity, pressure = sensor_manager.read_temperature_humidity()
        
        if temperature < -100:
            logger.error("Failed to read temperature")
            return False
        
        logger.info(f"Temperature: {temperature}°C")
        logger.info(f"Humidity: {humidity}%")
        logger.info(f"Pressure: {pressure} hPa")
        
        # Clean up
        sensor_manager.cleanup()
        
        return True
    except Exception as e:
        logger.error(f"Error testing BME280 sensor: {str(e)}")
        return False

def test_camera(config: Dict[str, Any]) -> bool:
    """Test the camera."""
    from sensors import SensorManager
    
    logger.info("Testing camera...")
    
    try:
        # Create sensor manager
        sensor_manager = SensorManager(config)
        
        # Capture image
        image_path = sensor_manager.capture_image()
        
        if not image_path:
            logger.error("Failed to capture image")
            return False
        
        logger.info(f"Image captured and saved to {image_path}")
        
        # Clean up
        sensor_manager.cleanup()
        
        return True
    except Exception as e:
        logger.error(f"Error testing camera: {str(e)}")
        return False

def test_water_pump(config: Dict[str, Any]) -> bool:
    """Test the water pump."""
    from actuators import ActuatorManager
    
    logger.info("Testing water pump...")
    
    try:
        # Create actuator manager
        actuator_manager = ActuatorManager(config)
        
        # Ask for confirmation
        print("\nWARNING: This will activate the water pump.")
        print("Make sure the pump is properly set up and won't cause any damage.")
        response = input("Proceed with pump test? (y/n): ")
        
        if response.lower() != 'y':
            logger.info("Pump test skipped by user")
            return True
        
        # Activate pump for a short time
        logger.info("Activating pump for 3 seconds...")
        success = actuator_manager.activate_pump(3)
        
        if not success:
            logger.error("Failed to activate water pump")
            return False
        
        logger.info("Pump activated successfully")
        
        # Clean up
        actuator_manager.cleanup()
        
        return True
    except Exception as e:
        logger.error(f"Error testing water pump: {str(e)}")
        return False

def test_weather_api(config: Dict[str, Any]) -> bool:
    """Test the weather API."""
    from weather import WeatherManager
    
    logger.info("Testing weather API...")
    
    try:
        # Create weather manager
        weather_manager = WeatherManager(config)
        
        # Get current weather
        current = weather_manager.get_current_weather()
        
        if not current:
            logger.error("Failed to get current weather")
            return False
        
        logger.info(f"Current weather: {current.get('weather', 'Unknown')} ({current.get('description', 'No description')})")
        logger.info(f"Temperature: {current.get('temperature', 'Unknown')}°C")
        
        # Get forecast
        forecast = weather_manager.get_forecast()
        
        if not forecast:
            logger.error("Failed to get weather forecast")
            return False
        
        logger.info(f"Forecast: {forecast.get('summary', 'No summary available')}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing weather API: {str(e)}")
        return False

def test_notifications(config: Dict[str, Any]) -> bool:
    """Test the notification system."""
    from notifications import NotificationManager
    
    logger.info("Testing notification system...")
    
    try:
        # Create notification manager
        notification_manager = NotificationManager(config)
        
        # Send test notification
        success = notification_manager.send_notification(
            "This is a test notification from the Smart Garden System",
            'info'
        )
        
        if not success and notification_manager.enabled:
            logger.warning("Notification was not sent, but notifications are enabled")
            logger.warning("Check your Telegram bot token and chat ID")
            return False
        elif not success:
            logger.info("Notifications are disabled, so no notification was sent")
            return True
        else:
            logger.info("Test notification sent successfully")
            return True
    except Exception as e:
        logger.error(f"Error testing notifications: {str(e)}")
        return False

def run_all_tests():
    """Run all hardware tests."""
    print("Smart Garden System - Hardware Test")
    print("==================================")
    
    # Load configuration
    config = load_config()
    
    # Run tests
    tests = [
        ("Soil Moisture Sensor", test_soil_moisture_sensor),
        ("BME280 Sensor", test_bme280_sensor),
        ("Camera", test_camera),
        ("Water Pump", test_water_pump),
        ("Weather API", test_weather_api),
        ("Notifications", test_notifications)
    ]
    
    results = {}
    
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        try:
            success = test_func(config)
            results[name] = success
        except Exception as e:
            logger.error(f"Unexpected error in {name} test: {str(e)}")
            results[name] = False
    
    # Print summary
    print("\nTest Results Summary")
    print("===================")
    
    all_passed = True
    for name, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{name}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\nAll tests passed! Your hardware setup is working correctly.")
    else:
        print("\nSome tests failed. Please check the logs for details.")

if __name__ == "__main__":
    run_all_tests()