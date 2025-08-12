import math
 
# Constants
EARTH_RADIUS = 6371000  # in meters
 
 
def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
 
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(lat1_rad) * \
        math.cos(lat2_rad) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = EARTH_RADIUS * c
 
    return distance
 
 
def calculate_bearing(lat1, lon1, lat2, lon2):
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
 
    dlon = lon2_rad - lon1_rad
 
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
 
    bearing_rad = math.atan2(y, x)
    bearing_deg = math.degrees(bearing_rad)
 
    # Normalize to [0, 360) degrees
    bearing_deg = (bearing_deg + 360) % 360
 
    return bearing_deg
 
 
def calculate_elevation(lat1, lon1, elev1, lat2, lon2, elev2):
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    elevation_rad = math.atan2(elev2 - elev1, distance)
    elevation_deg = math.degrees(elevation_rad)
    return elevation_deg
 
 
def calculate_slant_range(lat1, lon1, elev1, lat2, lon2, elev2):
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    slant_range = math.sqrt(distance**2 + (elev2 - elev1)**2)
    return slant_range
 
 
if __name__ == "__main__":
    # Input location 1
    lat1 = 41.072024
    lon1 = -112.025044
    elev1 = 1477
 
    # Input location 2
    lat2 = 41.072198
    lon2 = -112.025717
    elev2 = 1477
 
    # Calculate values
    distance_down_range = calculate_distance(lat1, lon1, lat2, lon2)
    bearing = calculate_bearing(lat1, lon1, lat2, lon2)
    elevation = calculate_elevation(lat1, lon1, elev1, lat2, lon2, elev2)
    slant_range = calculate_slant_range(lat1, lon1, elev1, lat2, lon2, elev2)
 
    # Output results
    print(f"\nFrom Location 1 to Location 2:")
    print(f"Bearing Degrees (True North): {bearing:.4f}")
    print(f"Elevation in Degrees: {elevation:.4f}")
    print(f"Down Range in Meters: {int(distance_down_range)}")
    print(f"Slant Range in Meters: {int(slant_range)}")