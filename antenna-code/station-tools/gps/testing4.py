import logging
import math
import time
import argparse
import os
import sys
from serial import Serial
import select
import curses

# Setup logging
logging.basicConfig(
    filename='gps_data.log',  # Log file
    level=logging.DEBUG,      # Log all messages at DEBUG level and above
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
)

# Function to calculate the azimuth between two GPS coordinates
def calculate_azimuth(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    delta_lon = lon2 - lon1
    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    azimuth = math.atan2(y, x)

    # Normalize azimuth to the range [0, 360]
    azimuth = math.degrees(azimuth)
    if azimuth < 0:
        azimuth += 360

    return azimuth

# Function to calculate the back azimuth (reverse azimuth)
def calculate_back_azimuth(azimuth):
    back_azimuth = azimuth + 180
    if back_azimuth >= 360:
        back_azimuth -= 360
    return back_azimuth

# Function to log GPS and waypoint data
def log_gps_data(local_data=None, waypoint_data=None, azimuth=None, back_azimuth=None):
    if local_data:
        logging.info(f"Local GPS Data: {local_data}")
    if waypoint_data:
        logging.info(f"Waypoint Data: {waypoint_data}")
    if azimuth is not None:
        logging.info(f"Calculated Azimuth: {azimuth:.2f} degrees")
    if back_azimuth is not None:
        logging.info(f"Calculated Back Azimuth: {back_azimuth:.2f} degrees")

# Parse arguments for logging flag
def parse_args():
    parser = argparse.ArgumentParser(description="GPS and Azimuth Calculation Script")
    parser.add_argument('--log', action='store_true', help="Enable logging of GPS and azimuth data")
    return parser.parse_args()

# Parse GNGGA data for local GPS
def parse_gngga(data):
    parts = data.split(',')
    time = parts[1]
    lat = float(parts[2]) / 100.0  # Convert to decimal degrees
    lon = float(parts[4]) / 100.0  # Convert to decimal degrees
    altitude = parts[9]
    return f"Time: {time}, Latitude: {lat}, Longitude: {lon}, Altitude: {altitude} m", lat, lon

# Parse GNWPL data for waypoint data
def parse_gnwpl(data):
    parts = data.split(',')
    lat = float(parts[1]) / 100.0  # Convert to decimal degrees
    lon = float(parts[3]) / 100.0  # Convert to decimal degrees
    waypoint = parts[5]
    return f"Waypoint: {waypoint} at Latitude: {lat}, Longitude: {lon}", lat, lon

# Main GPS reading loop
def read_serial_data(stdscr, log_flag):
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)   # Non-blocking input
    stdscr.timeout(100)  # 100ms timeout for refreshing the screen

    local_data = None
    waypoint_data = None
    azimuth = None
    back_azimuth = None
    lat1 = lon1 = lat2 = lon2 = None

    with Serial('/dev/ttyS0', 9600, timeout=1) as stream:
        while True:
            # Use select to check for incoming data without blocking
            rlist, _, _ = select.select([stream], [], [], 1.0)  # 1 second timeout for polling
            if rlist:
                line = stream.readline().decode('ascii', errors='replace').strip()
                if line.startswith('$GNGGA'):  # Local GPS data
                    local_data, lat1, lon1 = parse_gngga(line)
                elif line.startswith('$GNWPL'):  # Waypoint data
                    waypoint_data, lat2, lon2 = parse_gnwpl(line)
                    if lat1 and lon1 and lat2 and lon2:
                        # Calculate azimuth and back azimuth
                        azimuth = calculate_azimuth(lat1, lon1, lat2, lon2)
                        back_azimuth = calculate_back_azimuth(azimuth)
                        if log_flag:
                            log_gps_data(local_data=local_data, waypoint_data=waypoint_data, azimuth=azimuth, back_azimuth=back_azimuth)

            # Clear the screen and update display
            stdscr.clear()
            stdscr.addstr(0, 0, f"Local GPS Data: {local_data if local_data else 'Waiting for GPS...'}")
            stdscr.addstr(2, 0, f"Waypoint Data: {waypoint_data if waypoint_data else 'Waiting for Waypoint...'}")
            if azimuth is not None:
                stdscr.addstr(4, 0, f"Azimuth: {azimuth:.2f}°")
            if back_azimuth is not None:
                stdscr.addstr(6, 0, f"Back Azimuth: {back_azimuth:.2f}°")
            stdscr.refresh()

if __name__ == "__main__":
    args = parse_args()
    curses.wrapper(read_serial_data, log_flag=args.log)
