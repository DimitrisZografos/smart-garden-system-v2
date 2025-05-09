#!/usr/bin/env python3
"""
Smart Garden System - Startup Script
This script starts both the main garden system and the web interface.
"""

import os
import sys
import time
import argparse
import threading
import subprocess
import signal
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('startup')

# Global variables
processes = []

def start_main_system(simulate=True):
    """Start the main garden system"""
    logger.info("Starting main garden system...")
    
    cmd = [sys.executable, 'main.py']
    if simulate:
        cmd.append('--simulate')
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    processes.append(process)
    
    # Start a thread to read and log output
    def log_output():
        for line in process.stdout:
            logger.info(f"[MAIN] {line.strip()}")
    
    threading.Thread(target=log_output, daemon=True).start()
    
    return process

def start_web_interface():
    """Start the web interface"""
    logger.info("Starting web interface...")
    
    # Change to web_app directory
    web_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_app')
    
    process = subprocess.Popen(
        [sys.executable, 'app.py'],
        cwd=web_app_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    processes.append(process)
    
    # Start a thread to read and log output
    def log_output():
        for line in process.stdout:
            logger.info(f"[WEB] {line.strip()}")
    
    threading.Thread(target=log_output, daemon=True).start()
    
    return process

def cleanup(signum=None, frame=None):
    """Clean up processes on exit"""
    logger.info("Shutting down...")
    
    for process in processes:
        if process.poll() is None:  # Process is still running
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    
    logger.info("All processes terminated")
    sys.exit(0)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Start Smart Garden System')
    parser.add_argument('--no-simulate', action='store_true', help='Run with real hardware (not simulation)')
    args = parser.parse_args()
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # Start main system
        main_process = start_main_system(simulate=not args.no_simulate)
        
        # Wait a bit for the main system to initialize
        time.sleep(2)
        
        # Start web interface
        web_process = start_web_interface()
        
        # Get local IP address
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            ip_address = s.getsockname()[0]
        except Exception:
            ip_address = '127.0.0.1'
        finally:
            s.close()
        
        # Print access information
        print("\n" + "=" * 60)
        print(f"Smart Garden System is running!")
        print(f"Access the web interface at: http://{ip_address}:5000")
        print("=" * 60 + "\n")
        
        # Wait for processes to complete
        while True:
            if main_process.poll() is not None:
                logger.error("Main system process has terminated unexpectedly")
                break
            
            if web_process.poll() is not None:
                logger.error("Web interface process has terminated unexpectedly")
                break
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()