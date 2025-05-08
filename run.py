#!/usr/bin/env python3
"""
Run script for the Smart Garden System.
"""

import os
import sys
import time
import logging
import yaml
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run the Smart Garden System."""
    logger.info("Starting Smart Garden System")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Check if config.yaml exists
    if not os.path.exists('config.yaml'):
        logger.error("config.yaml not found. Please create it first.")
        sys.exit(1)
    
    # Import the main system (after ensuring directories exist)
    from src.main import SmartGardenSystem
    
    # Create and run the system
    system = SmartGardenSystem('config.yaml')
    
    # Start the system in a separate thread
    system_thread = threading.Thread(target=system.run)
    system_thread.daemon = True
    system_thread.start()
    
    # Print information about the system
    print("\n" + "="*80)
    print("Smart Garden System")
    print("="*80)
    print("\nThe system is now running.")
    print("Web interface available at: http://localhost:12000")
    print("\nPress Ctrl+C to exit.")
    print("="*80 + "\n")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    finally:
        logger.info("System stopped")

if __name__ == "__main__":
    main()