import json
import math
import re
import serial
import sys
import time
from aioconsole import ainput # type: ignore
import asyncio
from datetime import datetime

port = ['/dev/qtpy-data']
channel = None

color_names = {
    "aqua": (0, 255, 255),
    "black": (0, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 128, 0),
    "orange": (255, 165, 0),
    "pink": (240, 32, 128),
    "purple": (128, 0, 128),
    "red": (255, 0, 0),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
}

print("Enter a color in the format: (rrr,ggg,bbb)")
print("Example: (255,125,0) is orange")
print(" ".join([name for name in color_names]))

EARTH_RADIUS = 6371000  # in meters
# I Am going to need to find a way to get this info from some kind of lookup table or something. could also be something to put in using the dashboard. maybe time to work on that
MAG_DECLINATION = -11

def setup_serial():
    """
    Helper to connect and reconnet to the serial channel
    for outbound serial connection
    """
    global channel
    if channel is None:
        try:
            channel = serial.Serial(port[0])
            channel.timeout = 0.05
        except Exception as ex:
            print(ex)
            channel = None
    return channel


def error_serial():
    """
    Helper to handle serial errors
    for outbound serial connection
    """
    global channel
    if channel != None:
        channel.close()
        channel = None
        print("Exception on read, did the board disconnect ?")


async def read_serial():
    """
    Loop reading the serial IN and trea the message with a print
    """
    print("read_serial")
    while True:
        setup_serial()
        line = None
        try:
            line = channel.readline()[:-2]
        except KeyboardInterrupt:
            print("KeyboardInterrupt - quitting")
            exit()
        except:
            error_serial()
            await asyncio.sleep(1)
            continue

        data = {}
        if line != b"":
            try:
                data = json.loads(line.decode("utf8"))
            except:
                data = {"raw": line.decode("utf8")}

        # receive button information and print it out
        if "buttons" in data:
            for button in data["buttons"]:
                if button["status"] == "RELEASED":
                    print(f"Qtpy2040 Button {button['id']} clicked")

        # unidentified data sent by the board, helps with testing
        if "raw" in data:
            print(f"Board sent: {data['raw']}")

        await asyncio.sleep(0.1)


async def read_user():
    """
    a variety of user inputs, this will get converted to something I can control with mqtt
    this is more of a sometimes commands, this currently holds the command to set point at the remote node
    """
    data_out = []
    data_in = await ainput("> ")
    data_in = data_in.strip()
    print(data_in)

    if re.match("^\((\d+),(\d+),(\d+)\)$", data_in):
        # color formatted as (rrr,ggg,bbb)
        m = re.match("^\((\d+),(\d+),(\d+)\)$", data_in)
        color = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return json.dumps({"color": color})

    elif data_in.lower() in color_names:
        # color name for simple tests
        color = color_names[data_in.lower()]
        return json.dumps({"color": color})
    
    elif re.match("^(\d+)$", data_in):
        # send desired heading to micro controller
        m = re.match("^(\d+)$", data_in)
        heading = (int(m.group(1)))
        return json.dumps({"heading": heading})
    
    elif "bearing" in data_in:
        result = int(read_serial_data())
        if result is not None:
            return json.dumps({"heading": result})

    elif "exit" in data_in:
        sys.exit()
    
    else:
        # send whatever the user just vomited into the serial console. helpful for testing
        return json.dumps({"raw": data_in})

    # should not be reached
    return "\r\n"


async def send_serial():
    """
    Loop on a data provider (here a user prompt) and send the data.
    """
    print("send_serial")
    while True:
        setup_serial()
        user_string = await read_user()
        try:
            if user_string:
                channel.write((user_string + "\r\n").encode("utf8"))
        except Exception as ex:
            print(ex)
            error_serial()
        await asyncio.sleep(0.1)

def calculate_azimuth(lat1, lon1, lat2, lon2):
    # Currently this code is giving a back azimuth unless lat1 and lon1 are flipped with lat2 and lon2
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
    azimuth = ((bearing_deg + 360) % 360) + MAG_DECLINATION
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
    baud_rate1 = 9600
    max_wait_seconds = 60  # Maximum time to wait for data in seconds
    
    try:
        with serial.Serial(port, baud_rate1, timeout=1) as stream:
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
                    return int(round(azimuth))
                
    except serial.SerialException as e:
        print(f"Error accessing serial port: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None



boo = asyncio.ensure_future(read_serial())
baa = asyncio.ensure_future(send_serial())
loop = asyncio.get_event_loop()
loop.run_forever()

