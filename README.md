# Smart Garden System - University Project

A simplified smart garden monitoring and watering system designed for educational purposes. This project simulates a garden monitoring system with a single-page web interface.

## Overview

This project provides a simulated smart garden system that includes:

- Soil moisture monitoring
- Environmental monitoring (temperature, humidity, pressure)
- Automated watering system
- Plant image capture
- Weather forecast integration
- Single-page web interface for monitoring and control

The system is designed to run on a Raspberry Pi, but operates in simulation mode for educational purposes.

## Directory Structure

```
smart-garden-university-project/
├── config/               # Configuration files
├── data/                 # Data storage (images, sensor readings)
├── web_app/              # Web interface
│   ├── app.py            # Flask application with all functionality
│   ├── templates/        # Single HTML template
│   └── static/           # Static files (CSS, JS)
├── requirements.txt      # Python dependencies
├── run.sh                # Startup script
└── README.md             # This file
```

## Installation

1. Clone this repository to your Raspberry Pi:
   ```
   git clone https://github.com/yourusername/smart-garden-university-project.git
   cd smart-garden-university-project
   ```

2. Run the startup script:
   ```
   chmod +x run.sh
   ./run.sh
   ```

The script will:
- Create necessary directories
- Set up a default configuration
- Install required dependencies
- Start the web interface

## Web Interface

The web interface provides all functionality in a single page with tabs:

- **Dashboard**: Real-time sensor readings and system status
- **History**: Historical data visualization with charts
- **Images**: Gallery of plant images captured by the camera
- **Settings**: System configuration options

Access the web interface from any device on your local network:
```
http://<raspberry-pi-ip-address>:5000
```

Where `<raspberry-pi-ip-address>` is the IP address of your Raspberry Pi.

## Features

- **All-in-one design**: All functionality is contained in a single Python file and a single HTML page
- **Simulation mode**: No physical hardware required
- **Responsive interface**: Works on desktop and mobile devices
- **Real-time updates**: Sensor data refreshes automatically
- **Historical data**: Track changes over time
- **Image gallery**: View all captured plant images
- **Simple configuration**: Easy to customize settings

## Customization

You can customize the system by:

1. Editing the configuration file (`config/config.yaml`)
2. Modifying the web interface HTML (`web_app/templates/dashboard.html`)
3. Adjusting the simulation parameters in the app.py file

## License

This project is provided for educational purposes. Feel free to use and modify it for your university projects.