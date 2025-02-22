from serial import Serial
from pynmeagps import NMEAReader  # type: ignore

with Serial('/dev/ttyS0', 9600, timeout=3) as stream:
    nmr = NMEAReader(stream)
    while True:
        raw_data, parsed_data = nmr.read()
        print(f"RAW: {raw_data}")
        print(f"PARSED: {parsed_data}")
