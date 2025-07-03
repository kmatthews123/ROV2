### This didnt work lamo. going to node red
import asyncio
import json
import math
import re
import serial
import time
from datetime import datetime
from asyncio_mqtt import Client, MqttError
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
if not MQTT_BROKER:
    raise RuntimeError("Missing MQTT_BROKER in .env file")
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC_SUB = 'device/qtpy/out'
TOPIC_PUB = 'device/qtpy/in'
SERIAL_PORT = '/dev/qtpy-data'

channel = None

color_names = {
    "aqua": (0, 255, 255), "black": (0, 0, 0), "blue": (0, 0, 255),
    "green": (0, 128, 0), "orange": (255, 165, 0), "pink": (240, 32, 128),
    "purple": (128, 0, 128), "red": (255, 0, 0), "white": (255, 255, 255),
    "yellow": (255, 255, 0),
}

EARTH_RADIUS = 6371000
MAG_DECLINATION = -11

def setup_serial():
    global channel
    if channel is None:
        try:
            channel = serial.Serial(SERIAL_PORT, timeout=0.05)
        except Exception as ex:
            print(f"Serial setup error: {ex}")
            channel = None
    return channel

def error_serial():
    global channel
    if channel:
        channel.close()
        channel = None
        print("Serial error - channel closed")

async def read_serial_loop(mqtt_client):
    print("Serial read loop started")
    while True:
        setup_serial()
        try:
            line = channel.readline().strip()
        except Exception as e:
            error_serial()
            await asyncio.sleep(1)
            continue

        if not line:
            await asyncio.sleep(0.1)
            continue

        try:
            data = json.loads(line.decode('utf8'))
        except Exception:
            data = {"raw": line.decode('utf8')}

        if "buttons" in data:
            for button in data["buttons"]:
                if button["status"] == "RELEASED":
                    print(f"Button {button['id']} clicked")

        print("Sending to MQTT:", data)
        await mqtt_client.publish(TOPIC_PUB, json.dumps(data), qos=0)
        await asyncio.sleep(0.1)

async def mqtt_to_serial_loop(mqtt_client):
    print("MQTT subscription loop started")
    async with mqtt_client.messages() as messages:
        await mqtt_client.subscribe(TOPIC_SUB)
        async for message in messages:
            try:
                setup_serial()
                payload = message.payload.decode()
                print(f"MQTT IN: {payload}")
                if channel:
                    channel.write((payload + "\r\n").encode("utf8"))
            except Exception as e:
                print(f"MQTT-to-Serial error: {e}")
                error_serial()
            await asyncio.sleep(0.1)

def calculate_azimuth(lat1, lon1, lat2, lon2):
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlon = lon2_rad - lon1_rad
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360) % 360 + MAG_DECLINATION

def parse_gngga(data):
    parts = data.split(',')
    if len(parts) < 10: return None
    lat = float(parts[2]) / 100.0 * (1 if parts[3] == 'N' else -1)
    lon = float(parts[4]) / 100.0 * (1 if parts[5] == 'E' else -1)
    return lat, lon

def parse_gnwpl(data):
    parts = data.split(',')
    if len(parts) < 5: return None
    lat = float(parts[1]) / 100.0 * (1 if parts[2] == 'N' else -1)
    lon = float(parts[3]) / 100.0 * (1 if parts[4] == 'E' else -1)
    return lat, lon

async def main():
    try:
        async with Client(
            hostname=MQTT_BROKER,
            port=MQTT_PORT,
            username=MQTT_USER,
            password=MQTT_PASSWORD
        ) as mqtt_client:
            await asyncio.gather(
                read_serial_loop(mqtt_client),
                mqtt_to_serial_loop(mqtt_client)
            )
    except MqttError as e:
        print(f"MQTT connection error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
