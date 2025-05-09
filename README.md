# Smart Garden System - University Project

A simplified smart garden monitoring and watering system designed for educational purposes. This project simulates a complete garden monitoring system with sensors, actuators, and a web interface.

## Overview

This project provides a simulated smart garden system that includes:

- Soil moisture monitoring
- Environmental monitoring (temperature, humidity, pressure)
- Automated watering system
- Plant image capture
- Weather forecast integration
- Web interface for monitoring and control

The system is designed to run on a Raspberry Pi, but operates in simulation mode for educational purposes.

## Components

- **Sensors**: Simulated soil moisture and environmental sensors
- **Actuators**: Simulated watering system
- **Camera**: Simulated plant image capture
- **Weather**: Integration with weather forecast APIs
- **Web Interface**: Browser-based dashboard and control panel

## Directory Structure

```
smart-garden-university-project/
├── config/               # Configuration files
├── data/                 # Data storage (images, sensor readings)
├── sensors.py            # Sensor management
├── actuators.py          # Watering system control
├── weather.py            # Weather forecast integration
├── main.py               # Main program
├── web_app/              # Web interface
│   ├── app.py            # Flask application
│   ├── templates/        # HTML templates
│   └── static/           # Static files (CSS, JS, images)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Installation

1. Clone this repository to your Raspberry Pi or development machine:
   ```
   git clone https://github.com/yourusername/smart-garden-university-project.git
   cd smart-garden-university-project
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a configuration file:
   ```
   mkdir -p config
   cp config/config.yaml.example config/config.yaml
   ```

4. Edit the configuration file to match your preferences:
   ```
   nano config/config.yaml
   ```

## Usage

### Running the Main System

To start the main garden monitoring system:

```
python main.py
```

This will start the sensor monitoring, automated watering, and other core functions.

### Running the Web Interface

To start the web interface:

```
cd web_app
python app.py
```

Then access the web interface by opening a browser and navigating to:
```
http://<raspberry-pi-ip-address>:5000
```

Where `<raspberry-pi-ip-address>` is the IP address of your Raspberry Pi on your local network.

## Web Interface

The web interface provides:

- **Dashboard**: Real-time sensor readings and system status
- **History**: Historical data visualization with charts
- **Images**: Gallery of plant images captured by the camera
- **Settings**: System configuration options

You can access the web interface from any device on your local network by entering the Raspberry Pi's IP address and port 5000 in a web browser.

## Simulation Mode

This project operates in simulation mode, meaning:

- No actual hardware is required
- Sensor readings are simulated with realistic values
- Watering actions are simulated (no actual water pump control)
- Camera captures are simulated (sample images are used)

This makes it ideal for educational purposes and development without requiring physical hardware.

## Customization

You can customize the system by:

1. Modifying the configuration file (`config/config.yaml`)
2. Adjusting the simulation parameters in the code
3. Extending the functionality with new features
4. Customizing the web interface

## License

This project is provided for educational purposes. Feel free to use and modify it for your university projects.

## Acknowledgments

This project is a simplified version of a complete smart garden system, designed specifically for university coursework and educational purposes.