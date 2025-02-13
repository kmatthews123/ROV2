from Mikrotik_Connector import  MikrotikDevice
import time
import re

# this code is much slower for this purpous than the mikrotik api
# this is the code used initialy
# Create an instance of MikrotikDevice
device = MikrotikDevice()

# Connect to the MikroTik device
device.connect(ip_address="10.0.2.3", username="admin", password="yourpasswordhere", port="22")

 
def get_signal(self):
    # Get signal power and TX signal power
    output = self.send_command("/interface/wireless/registration-table/print stats detail")
    
    # Extract the values using regex
    signal_strength_match = re.search(r"signal-strength=(-?\d+dBm)", output)
    tx_signal_strength_match = re.search(r"tx-signal-strength=(-?\d+dBm)", output)

    # Get values or return None if not found
    signal_strength = signal_strength_match.group(1) if signal_strength_match else "N/A"
    tx_signal_strength = tx_signal_strength_match.group(1) if tx_signal_strength_match else "N/A"

    # Format output
    return f"Signal Strength: {signal_strength}, TX Signal Strength: {tx_signal_strength}"

try:
    while True:
        signal_strength=get_signal(device)
        print("device signal strength: ", signal_strength)
        time.sleep(0.05)
except KeyboardInterrupt:
    device.disconnect()
    print("\nGracefully exiting...")

