import pynmea2
import serial
import time
import math

# Smooth function for smoothing azimuth and back azimuth
def smooth_angle(new_angle, old_angle, smoothing_factor=0.1):
    if old_angle is None:
        return new_angle
    return old_angle + smoothing_factor * (new_angle - old_angle)

# Function to calculate the azimuth
def calculate_azimuth(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    azimuth = math.atan2(y, x)
    return math.degrees(azimuth) % 360

# Function to calculate back azimuth
def calculate_back_azimuth(azimuth):
    return (azimuth + 180) % 360

# Setup the serial connection to the GPS device
with serial.Serial('/dev/ttyS0', 9600, timeout=1) as ser:
    last_azimuth = None
    last_back_azimuth = None
    local_lat = None
    local_lon = None
    waypoint_lat = 47.011124
    waypoint_lon = -122.523796

    while True:
        line = ser.readline().decode('ascii', errors='replace').strip()
        if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
            try:
                msg = pynmea2.parse(line)
                local_lat = msg.latitude
                local_lon = msg.longitude
                time_received = msg.timestamp
                print(f"Time: {time_received}, Latitude: {local_lat}, Longitude: {local_lon}")

                # Calculate Azimuth and Back Azimuth
                if local_lat and local_lon:
                    azimuth = calculate_azimuth(local_lat, local_lon, waypoint_lat, waypoint_lon)
                    back_azimuth = calculate_back_azimuth(azimuth)

                    # Smooth the azimuth and back azimuth values
                    smoothed_azimuth = smooth_angle(azimuth, last_azimuth)
                    smoothed_back_azimuth = smooth_angle(back_azimuth, last_back_azimuth)

                    print(f"Calculated Azimuth: {smoothed_azimuth:.2f} degrees")
                    print(f"Calculated Back Azimuth: {smoothed_back_azimuth:.2f} degrees")

                    # Update the last azimuth and back azimuth
                    last_azimuth = smoothed_azimuth
                    last_back_azimuth = smoothed_back_azimuth

            except pynmea2.nmea.ParseError as e:
                print(f"Error parsing NMEA sentence: {e}")

        time.sleep(1)
