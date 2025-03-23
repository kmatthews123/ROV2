import serial

ser = serial.Serial('/dev/ttyS0', 9600, timeout=3)

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"RAW GPS DATA: {line}")