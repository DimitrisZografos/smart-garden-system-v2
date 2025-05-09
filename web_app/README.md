# Smart Garden System Web Interface

This directory contains the web interface for the Smart Garden System. The web interface allows you to monitor and control your garden system from any device on your local network.

## Features

- Real-time dashboard with sensor readings
- Historical data visualization
- Plant image gallery
- System settings configuration
- Manual watering control

## Setup

1. Make sure you have installed all the required dependencies:
   ```
   pip install -r ../requirements.txt
   ```

2. Run the web application:
   ```
   python app.py
   ```

3. Access the web interface by opening a browser and navigating to:
   ```
   http://<raspberry-pi-ip-address>:5000
   ```
   
   Where `<raspberry-pi-ip-address>` is the IP address of your Raspberry Pi on your local network.

## Directory Structure

- `app.py` - Main Flask application
- `templates/` - HTML templates
  - `layout.html` - Base template with common elements
  - `index.html` - Dashboard page
  - `history.html` - Historical data page
  - `images.html` - Plant images gallery
  - `settings.html` - System settings page
- `static/` - Static files
  - `css/` - CSS stylesheets
  - `js/` - JavaScript files
  - `images/` - Static images for the web interface

## Accessing from Your PC

The web interface is designed to run on the Raspberry Pi but be accessible from any device on your local network. To access it from your PC:

1. Make sure your PC and the Raspberry Pi are on the same network
2. Find the IP address of your Raspberry Pi (use `hostname -I` on the Pi)
3. Open a web browser on your PC
4. Enter `http://<raspberry-pi-ip-address>:5000` in the address bar

## Customization

You can customize the web interface by modifying the templates and static files. The web interface uses:

- Bootstrap 5 for styling
- Chart.js for data visualization
- JavaScript for dynamic content

## Troubleshooting

- If you can't access the web interface, make sure:
  - The Flask application is running on the Raspberry Pi
  - Your PC and the Raspberry Pi are on the same network
  - There are no firewall rules blocking the connection
  - You're using the correct IP address and port

- If the data isn't updating:
  - Check that the main Smart Garden System is running
  - Verify that the data directory exists and is writable
  - Check the system logs for any errors