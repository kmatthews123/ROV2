"""
Listens to the REPL port.
Receives color information and displays it on the NEOPIXEL.
Receives blink command and blinks once.
Sends button press and release.


This uses the optional second serial port available in Circuitpython 7.x
Activate it in the boot.py file with the following code

import usb_cdc
usb_cdc.enable(console=True, data=True)

Some boards might require disabling USB endpoints to enable the data port.
"""

import board # type: ignore
import neopixel # type: ignore
import digitalio # type: ignore
import json 
import time 
import usb_cdc # type: ignore

################################################################
# init board's LEDs for visual output
# replace with your own pins and stuff
################################################################

pix = None
if hasattr(board, "NEOPIXEL"):
    import neopixel
    pix = neopixel.NeoPixel(board.NEOPIXEL, 1)
    pix.fill((3, 0, 3))
else:
    print("This board is not equipped with a Neopixel.")


################################################################
# init board's button for acknowledging user interaction
# replace with your own pins and stuff
# - the code tries its best to find a default button
# - two fixed default values on some boards (for my tests)
################################################################

button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(digitalio.Pull.UP)
button_id = "BUTTON"

################################################################
# prepare values for the loop
################################################################

usb_cdc.data.timeout = 0.1
if button:
    button_past = button.value

################################################################
# Functions
################################################################
def simp_function(variable):
    if variable == True:
        print("recieved a thing")
        print(variable)
    else:
        print(variable)
        print("wut")

################################################################
# loop-y-loop
################################################################

while True:
    # add to that dictionary to send the data at the end of the loop
    data_out = {}

    # read the secondary serial line by line when there's data
    if usb_cdc.data.in_waiting > 0:
        data_in = usb_cdc.data.readline()

        # try to convert the data to a dict (with JSON)
        data = None
        if len(data_in) > 0:
            try:
                data = json.loads(data_in)
            except ValueError:
                data = {"raw": data_in.decode()}

        # interpret
        if isinstance(data, dict):

            # change the color of the neopixel
            if "color" in data:
                print(data["color"])
                if pix is not None:
                    pix.fill(data["color"])

            if "heading" in data:
                print("recieved heading")
                print(data["heading"])
                simp_function(data)

            else:
                print(data)

    # read the buttons and send the info to the serial
    if button and button_past != button.value:
        button_past = button.value
        if not button.value:
            data_out["buttons"] = [{"status": "PRESSED", "id": button_id}]
        else:
            data_out["buttons"] = [{"status": "RELEASED", "id": button_id}]

    # send the data out once everything to be sent is gathered
    if data_out:
        print(json.dumps(data_out))
        usb_cdc.data.write(json.dumps(data_out).encode() + b"\r\n")

    time.sleep(0.1)
