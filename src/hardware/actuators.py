"""
Actuator modules for the Smart Garden System.
"""

import time
import logging
import sys

logger = logging.getLogger(__name__)

# Try to import GPIO, but don't fail if it's not available (for development without hardware)
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    logger.info("RPi.GPIO is available - hardware mode enabled")
except ImportError:
    GPIO_AVAILABLE = False
    logger.warning("RPi.GPIO is not available - using message-based mode")

class WateringSystem:
    """
    Controls the water pump or solenoid valve for plant watering.
    """
    
    def __init__(self, pin: int, active_low: bool = False):
        """
        Initialize the watering system.
        
        Args:
            pin: The GPIO pin number connected to the relay
            active_low: Whether the relay is triggered by a LOW signal
        """
        self.pin = pin
        self.active_low = active_low
        self.is_watering = False
        
        # Initialize GPIO if available
        if GPIO_AVAILABLE:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.pin, GPIO.OUT)
                
                # Set initial state (off)
                if self.active_low:
                    GPIO.output(self.pin, GPIO.HIGH)
                else:
                    GPIO.output(self.pin, GPIO.LOW)
                    
                logger.info(f"Watering system initialized on pin {pin} (active_low={active_low})")
            except Exception as e:
                logger.error(f"Error initializing GPIO: {str(e)}")
                logger.warning("Falling back to message-based mode")
                GPIO_AVAILABLE = False
        else:
            logger.info(f"Watering system initialized in message-based mode (pin {pin})")
    
    def water(self, duration: int) -> None:
        """
        Activate the watering system for the specified duration.
        
        Args:
            duration: The duration in seconds to run the pump
        """
        if self.is_watering:
            logger.warning("Watering system is already active")
            return
            
        self.is_watering = True
        
        try:
            if GPIO_AVAILABLE:
                # Turn on the pump
                if self.active_low:
                    GPIO.output(self.pin, GPIO.LOW)
                else:
                    GPIO.output(self.pin, GPIO.HIGH)
                
                logger.info(f"Watering started for {duration} seconds")
                
                # Wait for the specified duration
                time.sleep(duration)
                
                # Turn off the pump
                if self.active_low:
                    GPIO.output(self.pin, GPIO.HIGH)
                else:
                    GPIO.output(self.pin, GPIO.LOW)
                
                logger.info("Watering completed")
            else:
                # Simulate watering in message-based mode
                logger.info(f"[SIMULATED] Watering started for {duration} seconds")
                
                # Simulate the delay
                time.sleep(duration)
                
                logger.info("[SIMULATED] Watering completed")
                
        except Exception as e:
            logger.error(f"Error during watering: {str(e)}")
        finally:
            self.is_watering = False
    
    def stop(self) -> None:
        """Stop watering immediately."""
        if not self.is_watering:
            return
            
        try:
            if GPIO_AVAILABLE:
                # Turn off the pump
                if self.active_low:
                    GPIO.output(self.pin, GPIO.HIGH)
                else:
                    GPIO.output(self.pin, GPIO.LOW)
                
                logger.info("Watering stopped")
            else:
                # Simulate stopping in message-based mode
                logger.info("[SIMULATED] Watering stopped")
                
        except Exception as e:
            logger.error(f"Error stopping watering: {str(e)}")
        finally:
            self.is_watering = False
    
    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        if GPIO_AVAILABLE:
            try:
                # Make sure the pump is off
                if self.active_low:
                    GPIO.output(self.pin, GPIO.HIGH)
                else:
                    GPIO.output(self.pin, GPIO.LOW)
                
                # Clean up the GPIO pin
                GPIO.cleanup(self.pin)
                
                logger.info("Watering system cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up GPIO: {str(e)}")
        else:
            logger.info("[SIMULATED] Watering system cleaned up")