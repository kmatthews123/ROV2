import math
import time
import serial
import sys
from datetime import datetime

EARTH_RADIUS = 6371000  # in meters

def calculate_azimuth(lat1, lon1, lat2, lon2):
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad)) - \
        (math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))
    
    bearing_rad = math.atan2(y, x)
    bearing_deg = math.degrees(bearing_rad)
    azimuth = (bearing_deg + 360) % 360
    return azimuth

def parse_gngga(data):
    parts = data.split(',')
    # print(parts)
    if len(parts) < 10:
        print("invalid sequence")
        return None
    
    if parts[3] == 'N':
        lat = float(parts[2]) / 100.0  # Convert to decimal degrees
    else:
        lat = float(parts[2]) / -100.0  # Convert to decimal degrees invert values if your south of the equator

    if parts[5] =='E':
        lon = float(parts[4]) / 100.0  # Convert to decimal degrees
    else:
        lon = float(parts[4]) / -100.0  # Convert to decimal degrees

    return lat, lon

def parse_gnwpl(data):
    parts = data.split(',')
    # print(parts)
    if len(parts) < 5:
        print("invalid sequence")
        return None
    
    if parts[2] == 'N':
        lat = float(parts[1]) / 100.0  # Convert to decimal degrees
    else:
        lat = float(parts[1]) / -100.0  # Convert to decimal degrees invert values if your south of the equator

    if parts[4] =='E':
        lon = float(parts[3]) / 100.0  # Convert to decimal degrees
    else:
        lon = float(parts[3]) / -100.0  # Convert to decimal degrees

    return lat, lon

def read_serial_data():
    port = '/dev/ttyS0'
    baud_rate = 9600
    max_wait_seconds = 60  # Maximum time to wait for data in seconds
    
    try:
        with serial.Serial(port, baud_rate, timeout=1) as stream:
            start_time = time.time()
            lat1, lon1 = None, None
            lat2, lon2 = None, None
            
            while True:
                elapsed_time = time.time() - start_time
                
                # Check if maximum wait time has been reached
                if elapsed_time > max_wait_seconds:
                    print("Maximum wait time exceeded. Exiting.")
                    return None
                
                line = stream.readline().decode('ascii', errors='replace').strip()
                
                if not line:
                    continue  # Skip empty lines
                    
                if line.startswith('$GNGGA'):
                    lat1, lon1 = parse_gngga(line)
                    print(f"Local GPS data received: Lat={lat1}, Lon={lon1}")
                    
                elif line.startswith('$GNWPL'):
                    lat2, lon2 = parse_gnwpl(line)
                    print(f"Waypoint data received: Lat={lat2}, Lon={lon2}")
                    
                if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
                    azimuth = calculate_azimuth(lat1, lon1, lat2, lon2)
                    print(f"Azimuth calculated: {azimuth} degrees")
                    return azimuth
                
    except serial.SerialException as e:
        print(f"Error accessing serial port: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    while True:
        try:
            result = read_serial_data()
            if result is not None:
                print(f"Azimuth: {result} degrees")
            else:
                print("Failed to calculate azimuth.")
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            sys.exit()