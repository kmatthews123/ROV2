import routeros_api
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MikroTik Router
connection = routeros_api.RouterOsApiPool(
    host = os.getenv("HOST") ,  # Change to your router's IP
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"),
    plaintext_login=True  # Ensure API login works without encryption
)

# Get API handle
api = connection.get_api()

try:
    while True:
        # Retrieve wireless registration data
        wireless_data = api.get_resource('/interface/wireless/registration-table')
        for entry in wireless_data.get():
            signal_strength = entry.get('signal-strength', 'N/A')
            tx_signal_strength = entry.get('tx-signal-strength', 'N/A')
            print(f"Signal Strength: {signal_strength}, TX Signal Strength: {tx_signal_strength}")

except KeyboardInterrupt:
    print("\nGracefully exiting...")
    connection.disconnect()
