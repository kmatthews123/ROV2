import serial
import threading
import time

# Define the serial ports and their baud rates
serial_port_1 = '/dev/ttyS0'
serial_port_2 = '/dev/ttyACM1'
baud_rate_1 = 9600
baud_rate_2 = 115200

# Function to read data from a given serial port
def read_serial(port, baud_rate, name):
    try:
        with serial.Serial(port, baudrate=baud_rate, timeout=1) as ser:
            while True:
                # Read line from the serial port
                data = ser.readline().decode('utf-8').strip()
                if data:
                    print(f"[{name}] {data}")
    except Exception as e:
        print(f"Error reading from {name}: {e}")

# Create threads for each serial port with their respective baud rates
thread1 = threading.Thread(target=read_serial, args=(serial_port_1, baud_rate_1, "Port 1 (ttyS0)"))
thread2 = threading.Thread(target=read_serial, args=(serial_port_2, baud_rate_2, "Port 2 (ttyACM1)"))

# Start the threads
thread1.start()
thread2.start()

# Keep the main program running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program interrupted")
    thread1.join()
    thread2.join()
