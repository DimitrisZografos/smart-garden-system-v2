#!/usr/bin/env python3
"""
Smart Garden System - Actuators Module
This module handles all actuator interactions for the Smart Garden System.
It provides a unified interface for controlling the watering system.

In simulation mode, it simulates watering actions instead of
controlling actual hardware.
"""

import time
import logging
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('actuators')

class WateringSystem:
    """Controls the watering system for the Smart Garden System"""
    
    def __init__(self, relay_pin=17, simulate=False):
        """
        Initialize the watering system
        
        Args:
            relay_pin (int): GPIO pin connected to the relay
            simulate (bool): If True, simulate watering instead of controlling hardware
        """
        self.relay_pin = relay_pin
        self.simulate = simulate
        self.is_watering = False
        self.watering_thread = None
        
        logger.info(f"Initializing WateringSystem (Simulation: {simulate})")
        
        # Initialize hardware if not in simulation mode
        if not simulate:
            try:
                import RPi.GPIO as GPIO
                
                # Set up GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.relay_pin, GPIO.OUT)
                GPIO.output(self.relay_pin, GPIO.HIGH)  # Relay is typically active LOW
                
                logger.info(f"Watering system initialized on GPIO pin {relay_pin}")
            except ImportError:
                logger.warning("RPi.GPIO library not available, falling back to simulation mode")
                self.simulate = True
            except Exception as e:
                logger.error(f"Error initializing watering system: {e}")
                self.simulate = True
    
    def water_plants(self, duration=10):
        """
        Water the plants for the specified duration
        
        Args:
            duration (int): Watering duration in seconds
        """
        if self.is_watering:
            logger.warning("Watering already in progress, ignoring request")
            print("[SIMULATION] Watering already in progress, ignoring request")
            return False
        
        # Start watering in a separate thread to avoid blocking
        self.watering_thread = threading.Thread(
            target=self._water_plants_thread,
            args=(duration,)
        )
        self.watering_thread.daemon = True
        self.watering_thread.start()
        
        return True
    
    def _water_plants_thread(self, duration):
        """
        Internal method to handle watering in a separate thread
        
        Args:
            duration (int): Watering duration in seconds
        """
        self.is_watering = True
        
        if self.simulate:
            logger.info(f"Simulating watering plants for {duration} seconds")
            print(f"[SIMULATION] Starting to water plants for {duration} seconds")
            time.sleep(duration)
            print(f"[SIMULATION] Finished watering plants after {duration} seconds")
        else:
            try:
                import RPi.GPIO as GPIO
                
                logger.info(f"Watering plants for {duration} seconds")
                # Turn on pump (relay is active LOW)
                GPIO.output(self.relay_pin, GPIO.LOW)
                time.sleep(duration)
                # Turn off pump
                GPIO.output(self.relay_pin, GPIO.HIGH)
                logger.info("Watering completed")
            except Exception as e:
                logger.error(f"Error during watering: {e}")
        
        self.is_watering = False
    
    def stop_watering(self):
        """
        Stop watering immediately
        
        Returns:
            bool: True if watering was stopped, False if not watering
        """
        if not self.is_watering:
            return False
        
        if self.simulate:
            logger.info("Simulating stopping watering")
            print("[SIMULATION] Stopping watering")
        else:
            try:
                import RPi.GPIO as GPIO
                
                logger.info("Stopping watering")
                # Turn off pump
                GPIO.output(self.relay_pin, GPIO.HIGH)
            except Exception as e:
                logger.error(f"Error stopping watering: {e}")
        
        # The thread will still be running, but the next time it checks
        # is_watering it will exit
        self.is_watering = False
        return True
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if not self.simulate:
            try:
                import RPi.GPIO as GPIO
                
                # Make sure pump is off
                GPIO.output(self.relay_pin, GPIO.HIGH)
                # Clean up GPIO
                GPIO.cleanup(self.relay_pin)
                logger.info("Watering system cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up watering system: {e}")

if __name__ == "__main__":
    # Simple test code
    watering_system = WateringSystem(simulate=True)
    
    print("Testing watering system...")
    print("Watering for 5 seconds...")
    watering_system.water_plants(duration=5)
    
    # Wait for watering to complete
    time.sleep(6)
    
    print("Testing watering system again...")
    print("Watering for 10 seconds...")
    watering_system.water_plants(duration=10)
    
    # Wait for 3 seconds and then stop
    time.sleep(3)
    print("Stopping watering early...")
    watering_system.stop_watering()
    
    # Clean up
    watering_system.cleanup()