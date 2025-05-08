# Smart Garden System

## Installation Guide

This guide provides step-by-step instructions for installing and configuring the Smart Garden System.

### Prerequisites

- Raspberry Pi (3B+ or 4 recommended) with Raspberry Pi OS installed
- Python 3.7 or higher
- Internet connection for initial setup
- Hardware components as listed in [HARDWARE_SETUP.md](HARDWARE_SETUP.md)

### Step 1: Clone the Repository

```bash
git clone https://github.com/DimitrisZografos/smart-garden-system.git
cd smart-garden-system
```


### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install hardware-specific libraries
pip install RPi.GPIO adafruit-circuitpython-bme280 picamera
```


### Step 3: Enable Required Interfaces

```bash
sudo raspi-config
```


Navigate to "Interfacing Options" and enable both I2C and Camera interfaces if you're using them.

### Step 4: Configure the System

1. Copy the example configuration file:

```bash
cp config.yaml.example config.yaml
```


2. Edit the configuration file with your settings:

```bash
nano config.yaml
```



3. Configure the following required settings:

   - Weather API key (if using weather-aware watering)
   - Telegram bot token and chat ID (if using Telegram notifications)
   - Database credentials (if using PostgreSQL)

### Step 5: Test the Hardware

Run the hardware test scripts to ensure everything is connected properly:

```bash
# Test soil moisture sensor
python tests/test_soil_moisture.py

# Test BME280 sensor
python tests/test_bme280.py

# Test relay/pump
python tests/test_relay.py

# Test camera
python tests/test_camera.py
```


### Step 6: Run the System

You can set up the system as a service:

1. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/smart-garden.service
```



2. Add the following content (adjust paths as needed):

```
[Unit]
Description=Smart Garden System
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/smart-garden-system
ExecStart=/usr/bin/python3 /home/pi/smart-garden-system/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```



3. Enable and start the service:

```bash
sudo systemctl enable smart-garden.service
sudo systemctl start smart-garden.service
```



4. Check the service status:

```bash
sudo systemctl status smart-garden.service
```



### Step 7: Set Up Telegram Notifications (Optional)

If you want to use Telegram for notifications:

1. Create a Telegram bot using BotFather:
   - Open Telegram and search for @BotFather
   - Send /newbot and follow the instructions
   - Copy the bot token provided

2. Get your chat ID:
   - Send a message to @userinfobot
   - Copy the ID number provided

3. Update your config.yaml with the bot token and chat ID:

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
```



### Step 8: Access the Web Interface

If you've enabled the web interface, you can access it at:

```
http://your-raspberry-pi-ip:12000
```



Replace "your-raspberry-pi-ip" with the IP address of your Raspberry Pi.

### Troubleshooting

If you encounter issues during installation or operation:

1. Check the logs:

```bash
sudo journalctl -u smart-garden.service
```



2. Verify hardware connections as described in [HARDWARE_SETUP.md](HARDWARE_SETUP.md)

3. Ensure all required services are running:

```bash
sudo systemctl status smart-garden.service
```



4. For more detailed troubleshooting, refer to the [HARDWARE_SETUP.md](HARDWARE_SETUP.md) file.
