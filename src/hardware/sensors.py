"""
Sensor modules for the Smart Garden System.
"""

import time
import random
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Try to import hardware-specific libraries, but don't fail if they're not available
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logger.error("RPi.GPIO is not available - hardware functionality will not work")

try:
    import board
    import busio
    import adafruit_bme280.advanced as adafruit_bme280
    BME280_AVAILABLE = True
except ImportError:
    BME280_AVAILABLE = False
    logger.error("adafruit_bme280 is not available - BME280 sensor will not work")

try:
    import picamera
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False
    logger.error("picamera is not available - camera functionality will not work")

class SoilMoistureSensor:
    """
    Interface for soil moisture sensor.
    """
    
    def __init__(self, pin: int, dry_value: int = 800, wet_value: int = 300):
        """
        Initialize the soil moisture sensor.
        
        Args:
            pin: The GPIO pin number connected to the sensor
            dry_value: The sensor value when completely dry
            wet_value: The sensor value when in water
        """
        self.pin = pin
        self.dry_value = dry_value
        self.wet_value = wet_value
        
        # Range for converting raw values to percentages
        self.value_range = self.dry_value - self.wet_value
        
        if GPIO_AVAILABLE:
            try:
                # For a real implementation, you might need an ADC
                # This is just a placeholder for the actual hardware setup
                logger.info(f"Soil moisture sensor initialized on pin {pin}")
            except Exception as e:
                logger.error(f"Error initializing soil moisture sensor: {str(e)}")
                logger.warning("Falling back to simulated mode")
                GPIO_AVAILABLE = False
        else:
            logger.warning("Soil moisture sensor initialized without hardware support - please install RPi.GPIO")
    
    def read_raw(self) -> int:
        """
        Read the raw value from the sensor.
        
        Returns:
            The raw sensor value
        """
        if GPIO_AVAILABLE:
            try:
                # This is a placeholder for actual hardware reading
                # In a real implementation, you would read from an ADC
                # For now, we'll just return a simulated value
                return random.randint(self.wet_value, self.dry_value)
            except Exception as e:
                logger.error(f"Error reading soil moisture sensor: {str(e)}")
                return self._simulate_reading()
        else:
            return self._simulate_reading()
    
    def read_percentage(self) -> float:
        """
        Read the soil moisture as a percentage (0-100%).
        
        Returns:
            The soil moisture percentage (0% = dry, 100% = wet)
        """
        raw_value = self.read_raw()
        
        # Convert to percentage (0% = dry, 100% = wet)
        if self.value_range == 0:
            return 0
            
        moisture = 100 - ((raw_value - self.wet_value) / self.value_range * 100)
        
        # Clamp to 0-100%
        moisture = max(0, min(100, moisture))
        
        return moisture
    
    def _simulate_reading(self) -> int:
        """
        Fallback when hardware reading fails.
        
        Raises:
            RuntimeError: Always raised as hardware is required
        """
        logger.error("Cannot read soil moisture: hardware not available")
        raise RuntimeError("Soil moisture sensor hardware not available")

class BME280Sensor:
    """
    Interface for BME280 temperature, humidity, and pressure sensor.
    """
    
    def __init__(self, i2c_address: str = "0x76"):
        """
        Initialize the BME280 sensor.
        
        Args:
            i2c_address: The I2C address of the sensor (usually 0x76 or 0x77)
        """
        self.i2c_address = int(i2c_address, 16)
        self.sensor = None
        
        if BME280_AVAILABLE:
            try:
                # Initialize I2C bus and sensor
                i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=self.i2c_address)
                
                # Configure the sensor
                self.sensor.sea_level_pressure = 1013.25  # Standard sea level pressure in hPa
                
                logger.info(f"BME280 sensor initialized at address {i2c_address}")
            except Exception as e:
                logger.error(f"Error initializing BME280 sensor: {str(e)}")
                logger.warning("Falling back to simulated mode")
                BME280_AVAILABLE = False
                self.sensor = None
        else:
            logger.warning("BME280 sensor initialized without hardware support - please install adafruit_bme280")
    
    def read(self) -> Dict[str, float]:
        """
        Read temperature, humidity, and pressure from the sensor.
        
        Returns:
            Dictionary with temperature (°C), humidity (%), and pressure (hPa)
        """
        if BME280_AVAILABLE and self.sensor:
            try:
                return {
                    'temperature': round(self.sensor.temperature, 1),
                    'humidity': round(self.sensor.humidity, 1),
                    'pressure': round(self.sensor.pressure, 1)
                }
            except Exception as e:
                logger.error(f"Error reading BME280 sensor: {str(e)}")
                return self._simulate_reading()
        else:
            return self._simulate_reading()
    
    def _simulate_reading(self) -> Dict[str, float]:
        """
        Fallback when hardware reading fails.
        
        Raises:
            RuntimeError: Always raised as hardware is required
        """
        logger.error("Cannot read BME280 sensor: hardware not available")
        raise RuntimeError("BME280 sensor hardware not available")

class Camera:
    """
    Interface for Raspberry Pi camera.
    """
    
    def __init__(self, resolution: Tuple[int, int] = (1280, 720)):
        """
        Initialize the camera.
        
        Args:
            resolution: The image resolution as (width, height)
        """
        self.resolution = resolution
        self.camera = None
        
        if CAMERA_AVAILABLE:
            try:
                self.camera = picamera.PiCamera()
                self.camera.resolution = resolution
                
                # Allow the camera to warm up
                time.sleep(2)
                
                logger.info(f"Camera initialized with resolution {resolution}")
            except Exception as e:
                logger.error(f"Error initializing camera: {str(e)}")
                logger.warning("Falling back to simulated mode")
                CAMERA_AVAILABLE = False
                self.camera = None
        else:
            logger.warning("Camera initialized without hardware support - please install picamera")
    
    def capture(self, output_path: str) -> bool:
        """
        Capture an image and save it to the specified path.
        
        Args:
            output_path: The path to save the image to
            
        Returns:
            True if successful, False otherwise
        """
        if CAMERA_AVAILABLE and self.camera:
            try:
                self.camera.capture(output_path)
                logger.info(f"Image captured and saved to {output_path}")
                return True
            except Exception as e:
                logger.error(f"Error capturing image: {str(e)}")
                return self._simulate_capture(output_path)
        else:
            return self._simulate_capture(output_path)
    
    def _simulate_capture(self, output_path: str) -> bool:
        """
        Fallback when hardware capture fails.
        
        Args:
            output_path: The path where the image would be saved
            
        Raises:
            RuntimeError: Always raised as hardware is required
        """
        logger.error("Cannot capture image: camera hardware not available")
        raise RuntimeError("Camera hardware not available")
    
    def close(self) -> None:
        """Close the camera and release resources."""
        if CAMERA_AVAILABLE and self.camera:
            try:
                self.camera.close()
                logger.info("Camera closed")
            except Exception as e:
                logger.error(f"Error closing camera: {str(e)}")