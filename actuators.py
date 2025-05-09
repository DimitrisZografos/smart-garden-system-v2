"""
Smart Garden System - Actuator Module (Simulation Only)
Created by: Dimitris Zografos
Date: May 2025

This module simulates actuator interactions for the Smart Garden System.
It provides functions to simulate watering actions with display messages
instead of controlling actual hardware.
"""

import time
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('actuators')

class ActuatorManager:
    """
    Simulates actuators in the Smart Garden System.
    
    This class provides methods to simulate actuator actions and display
    messages about what would happen with real hardware.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the actuator manager with the provided configuration.
        
        Args:
            config: Dictionary containing actuator configuration from config.yaml
        """
        self.config = config
        self.hardware_config = config.get('hardware', {})
        self.pump_config = self.hardware_config.get('pump', {})
        self.pump_duration = self.pump_config.get('duration', 10)  # seconds
        
        logger.info("Actuator simulation initialized (no hardware control)")
    
    def activate_pump(self, duration: int = None) -> bool:
        """
        Simulate activating the water pump for the specified duration.
        
        Args:
            duration: Duration in seconds to simulate running the pump. 
                     If None, use the configured duration.
            
        Returns:
            True to indicate successful simulation
        """
        if duration is None:
            duration = self.pump_duration
        
        # Display message about what would happen with real hardware
        message = f"SIMULATION: Water pump would activate for {duration} seconds"
        print(message)
        logger.info(message)
        
        # Simulate the time it would take
        time.sleep(1)  # Just a short delay for simulation
        
        # Display completion message
        message = "SIMULATION: Water pump would now deactivate"
        print(message)
        logger.info(message)
        
        return True
    
    def water_plants(self, soil_moisture: int) -> bool:
        """
        Simulate watering the plants if the soil moisture is below the threshold.
        
        Args:
            soil_moisture: Current soil moisture percentage
            
        Returns:
            True if watering would be performed, False otherwise
        """
        # Get threshold from configuration
        threshold = self.hardware_config.get('soil_moisture', {}).get('threshold', 30)
        
        # Check if watering is needed
        if soil_moisture < threshold:
            message = f"DECISION: Soil moisture ({soil_moisture}%) below threshold ({threshold}%). Plants need watering."
            print(message)
            logger.info(message)
            return self.activate_pump()
        else:
            message = f"DECISION: Soil moisture ({soil_moisture}%) above threshold ({threshold}%). No watering needed."
            print(message)
            logger.info(message)
            return False
    
    def cleanup(self) -> None:
        """Clean up resources when shutting down."""
        logger.info("Actuator simulation cleaned up")


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
    
    # Create actuator manager
    actuator_manager = ActuatorManager(config)
    
    # Test pump activation
    print("Testing water pump (5 seconds)...")
    actuator_manager.activate_pump(5)
    
    # Test watering logic
    test_moisture_levels = [10, 20, 30, 40, 50]
    for moisture in test_moisture_levels:
        print(f"\nTesting with soil moisture: {moisture}%")
        watered = actuator_manager.water_plants(moisture)
        if watered:
            print("Plants were watered")
        else:
            print("No watering needed")
    
    # Clean up
    actuator_manager.cleanup()