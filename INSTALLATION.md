# Smart Garden System

## Installation Guide

This guide provides step-by-step instructions for installing and configuring the Smart Garden System.

### Prerequisites

- Raspberry Pi (3B+ or 4 recommended) with Raspberry Pi OS installed
- Python 3.7 or higher
- Internet connection for initial setup
- Hardware components as listed in [HARDWARE_SETUP.md](HARDWARE_SETUP.md)

### Step 1: Clone the Repository



### Step 2: Install Dependencies



### Step 3: Enable Required Interfaces



Navigate to "Interfacing Options" and enable both I2C and Camera interfaces if you're using them.

### Step 4: Configure the System

1. Copy the example configuration file:



2. Edit the configuration file with your settings:



3. Configure the following required settings:

   - Weather API key (if using weather-aware watering)
   - Telegram bot token and chat ID (if using Telegram notifications)
   - Database credentials (if using PostgreSQL)

### Step 5: Test the Hardware

Run the hardware test scripts to ensure everything is connected properly:



### Step 6: Run the System

For testing and development, you can run the system in demo mode:



For production use, you can set up the system as a service:

1. Create a systemd service file:



2. Add the following content (adjust paths as needed):



3. Enable and start the service:



4. Check the service status:



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



### Step 8: Access the Web Interface

If you've enabled the web interface, you can access it at:



Replace "your-raspberry-pi-ip" with the IP address of your Raspberry Pi.

### Troubleshooting

If you encounter issues during installation or operation:

1. Check the logs:



2. Verify hardware connections as described in [HARDWARE_SETUP.md](HARDWARE_SETUP.md)

3. Ensure all required services are running:



4. For more detailed troubleshooting, refer to the [HARDWARE_SETUP.md](HARDWARE_SETUP.md) file.
