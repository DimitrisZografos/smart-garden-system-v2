# Smart Garden University Project

A simplified smart garden monitoring and control system designed for educational purposes. This project provides a simulation-based approach to learning about IoT systems, sensors, and web interfaces without requiring actual hardware.

## Features

- **Simulation Mode**: All hardware interactions are simulated with display messages
- **Camera Integration**: Camera component is required but can be simulated
- **Web Interface**: Complete web application for monitoring and control
- **Educational Focus**: Designed for university projects and learning

## Download

The complete project is available as a zip file in this repository:

[Download Smart Garden University Project](https://github.com/DimitrisZografos/smart-garden-system-v2/raw/university-project-v3-new/smart_garden_university_project.zip)

## Project Structure

```
smart-garden-university-project/
├── config/                  # Configuration files
├── data/                    # Data storage directory
├── web_app/                 # Web interface files
│   ├── static/              # CSS, JS, and images
│   ├── templates/           # HTML templates
│   └── app.py               # Flask application
├── actuators.py             # Actuator control (simulated)
├── sensors.py               # Sensor interfaces (simulated)
├── weather.py               # Weather data retrieval
├── main.py                  # Main system logic
├── start.py                 # Combined startup script
└── requirements.txt         # Python dependencies
```

## Installation

1. Download and extract the zip file
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the system:
   ```
   python start.py
   ```

## Web Interface

The web interface runs on port 5000 by default and provides:

- Dashboard with current readings
- History page with sensor data over time
- Images page to view captured images
- Settings page to configure the system

## License

This project is available for educational purposes.