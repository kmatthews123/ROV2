import logging
import math
import time
import argparse
import os
import sys
from serial import Serial
import select

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

# Function to log GPS and waypoint data
def log_gps_data(local_data=None, waypoint_data=None, azimuth=None):
    if local_data:
        logging.info(f"Local GPS Data: {local_data}")
    if waypoint_data:
        logging.info(f"Waypoint Data: {waypoint_data}")
    if azimuth is not None:
        logging.info(f"Calculated Azimuth: {azimuth:.2f} degrees")

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
def read_serial_data(log_flag):
    with Serial('/dev/ttyS0', 9600, timeout=1) as stream:
        local_data = None
        waypoint_data = None

        while True:
            # Use select to check for incoming data without blocking
            rlist, _, _ = select.select([stream], [], [], 1.0)  # 1 second timeout for polling
            if rlist:
                line = stream.readline().decode('ascii', errors='replace').strip()
                if line.startswith('$GNGGA'):  # Local GPS data
                    local_data, lat1, lon1 = parse_gngga(line)
                elif line.startswith('$GNWPL'):  # Waypoint data
                    waypoint_data, lat2, lon2 = parse_gnwpl(line)
                    if local_data and waypoint_data:
                        # Calculate azimuth between local GPS and waypoint
                        azimuth = calculate_azimuth(lat1, lon1, lat2, lon2)
                        if log_flag:
                            log_gps_data(local_data=local_data, waypoint_data=waypoint_data, azimuth=azimuth)
                        # Display on terminal
                        print(local_data)
                        print(waypoint_data)
                        print(f"Calculated Azimuth: {azimuth:.2f} degrees")
            # Periodically refresh the terminal, making it less static
            time.sleep(0.1)

if __name__ == "__main__":
    args = parse_args()
    read_serial_data(log_flag=args.log)
