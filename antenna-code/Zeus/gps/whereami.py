from serial import Serial
from pynmeagps import NMEAReader # type: ignore
import time

# test
# Stream info recived from meshtastic gps via uart connection

while True:
  with Serial('/dev/ttyS0', 9600) as stream:
    nmr = NMEAReader(stream)
    raw_data, parsed_data = nmr.read()
    if parsed_data is not None:
      print(parsed_data)
      time.sleep(0.5)