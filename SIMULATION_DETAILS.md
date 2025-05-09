# Simulation Details

This document explains the simulation aspects of the Smart Garden System project.

## Overview

This version of the Smart Garden System is designed for educational purposes, focusing on the software architecture and decision-making logic without requiring actual hardware control. Instead of controlling physical actuators, the system displays messages about what actions would be taken based on sensor readings.

## Simulated Components

### Actuators

The `actuators.py` module has been modified to:
- Remove all hardware control code (no GPIO manipulation)
- Replace actual watering actions with descriptive console messages
- Simulate the decision-making process for when to water plants
- Provide clear output about what would happen with real hardware

Example output:
```
DECISION: Soil moisture (25%) below threshold (30%). Plants need watering.
SIMULATION: Water pump would activate for 10 seconds
SIMULATION: Water pump would now deactivate
```

### Camera (Required Component)

The camera is a required component in this project. The `sensors.py` module has been updated to:
- Always attempt to use the camera if available
- Create simulated plant images if a physical camera is not available
- Generate visually interesting simulated images with plant-like features
- Include timestamp and other relevant information in the images

The simulated images provide a visual representation of what the system is monitoring, making the project more engaging even without physical hardware.

### Sensors

When running in simulation mode (no hardware available), the system:
- Generates realistic random values for soil moisture, temperature, humidity, and pressure
- Logs these values as if they were read from actual sensors
- Makes watering decisions based on these simulated readings

## Educational Value

This simulation-focused approach offers several educational benefits:

1. **Focus on Software Architecture**: Students can concentrate on understanding the system's architecture, data flow, and decision-making logic without hardware complications.

2. **Easier Testing**: The simulation allows for testing various scenarios by manipulating the simulated sensor values.

3. **Accessibility**: Students without access to all the hardware components can still fully participate in the project.

4. **Visualization**: The simulated plant images provide a visual element that helps understand what the system is monitoring.

5. **Preparation for Hardware Implementation**: The code structure is designed to make it easy to replace simulated components with real hardware control in the future.

## Running in Simulation Mode

The system automatically detects whether hardware libraries are available and switches to simulation mode if they are not. This means you can run the project on any computer with Python installed, not just a Raspberry Pi.

To force simulation mode even on a Raspberry Pi, you can modify the `HARDWARE_AVAILABLE` flag in the code:

```python
# Force simulation mode
HARDWARE_AVAILABLE = False
```

## Adding Real Hardware

The project is designed to make it easy to transition from simulation to real hardware control. The code structure separates hardware-specific functionality, making it straightforward to replace simulated components with real ones as they become available.

For guidance on setting up real hardware, refer to the `HARDWARE_SETUP.md` file.