# writen by keith matthews using examples from adafruit librarys

import board #type: ignore
import digitalio #type: ignore
import time
import math
import adafruit_lis2mdl # type: ignore
import usb_cdc # type: ignore
# import random
import neopixel
import json

# Setup pins as outputs or inputs

# Stepper
# Define GPIO pins for motor control and endstops
direction_pin = digitalio.DigitalInOut(board.D0)
step_pin = digitalio.DigitalInOut(board.D1)
direction_pin.direction = digitalio.Direction.OUTPUT
step_pin.direction = digitalio.Direction.OUTPUT
# Define motor directions at start of program
FORWARD = True
REVERSE = False
# Setup microstepping pins
MS1 = digitalio.DigitalInOut(board.D3)
MS2 = digitalio.DigitalInOut(board.D2)
MS1.direction = digitalio.Direction.OUTPUT
MS2.direction = digitalio.Direction.OUTPUT

#magnetometer
# i2c = board.I2C()
i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
magnetometer = adafruit_lis2mdl.LIS2MDL(i2c)

#USB serial data
#Access the USB serial port
usb_cdc.data.timeout = 0.1
# usb_serial = usb_cdc.data

#Neopixel setup
pix = neopixel.NeoPixel(board.NEOPIXEL, 1)
pix.fill((3, 0, 3))

#Boot button added as input
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(digitalio.Pull.UP)
button_id = "BUTTON"
if button:
    button_past = button.value

# Variables
# magnetometer
# adjust based on location and random shit in the area 
# magnetometer calibration value
hardiron_calibration = [[-32.7, 10.2], [-4.95, 36.45], [-24.15, -17.25]] 
#headings are sloppy this handles the slop +- 3 degrees of slop seems normal with propper calibration
acceptable_range = 0
# stepper
# step delay min and max for smoothing movement to desired heading
MIN_STEP_DELAY = 0.001  # Fastest stepping speed
MAX_STEP_DELAY = 0.001009   # Slowest stepping speed

# begin functions

# This will take the magnetometer values, adjust them with the calibrations
# and return a new array with the XYZ values ranging from -100 to 100
def normalize(_magvals):

    ret = [0, 0, 0]

    for i, axis in enumerate(_magvals):

        minv, maxv = hardiron_calibration[i]

        axis = min(max(minv, axis), maxv)  # keep within min/max calibration

        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100

    return ret

# not using this yet but this is used to calibrate the magnetometer based on nearby magnetic objects that can throw it off
def calibrate_hardiorn():
    hardiron_calibration = [[1000, -1000], [1000, -1000], [1000, -1000]]
    print("Prepare to calibrate! Twist the magnetometer around in 3D in...")
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)   
    start_time = time.monotonic()
    # Update the high and low extremes
    while time.monotonic() - start_time < 10.0:
        magval = magnetometer.magnetic
        print("Calibrating - X:{0:10.2f}, Y:{1:10.2f}, Z:{2:10.2f} uT".format(*magval))
        for i, axis in enumerate(magval):
            hardiron_calibration[i][0] = min(hardiron_calibration[i][0], axis)
            hardiron_calibration[i][1] = max(hardiron_calibration[i][1], axis)
    print("Calibration complete:")
    print("hardiron_calibration =", hardiron_calibration)
    return hardiron_calibration

def set_microstep_div(step_div):
# Define microstepping values
# step selection table
# |  MS1   |  MS2   | Microstep Resolution
# |  False |  False | 1/8 fast
# |  False |  True  | 1/2 medium slow
# |  True  |  False | 1/4 medium (I think?)
# |  True  |  True  | 1/16 most slow (I think?)
    microstep_config = {
        8: {'MS1': False, 'MS2': False},
        2: {'MS1': False, 'MS2': True},
        4: {'MS1': True, 'MS2': False},
        16: {'MS1': True, 'MS2': True}
    }
    
    if step_div in microstep_config:
        global MS1, MS2
        MS1.value = microstep_config[step_div]['MS1']
        MS2.value = microstep_config[step_div]['MS2']
        # print(f"set microstep value to {step_div}")
    else:
        global MS1, MS2
        MS1.value = False
        MS2.value = False
        # print("unknown microstep value selected, setting to 1/8")
        
def set_direction(direction):
    direction_pin.value = direction
   # print(direction_pin.value)

def step(step_delay):
    step_pin.value = True
    time.sleep(step_delay)  # Pulse width
    step_pin.value = False

def get_heading():
    magvals = magnetometer.magnetic
    normvals = normalize(magvals)
    # print("magnetometer: %s -> %s" % (magvals, normvals))
    # we will only use X and Y for the compass calculations, so hold it level!
    compass_heading = int(math.atan2(normvals[1], normvals[0]) * 180.0 / math.pi)
    # compass_heading is between -180 and +180 since atan2 returns -pi to +pi
    # this translates it to be between 0 and 360
    compass_heading += 180
    #print("Heading:", compass_heading)
    return compass_heading

# This works but with no smoothing steps, abrupt stops, and no slop handling
# This would probably be fine to use tbh, unless I figure out full steps...
# def gotoheading(Desired_Heading):
#     while get_heading() != Desired_Heading:
        
#         current_heading = get_heading()
#         heading_diff = (Desired_Heading - current_heading) % 360
        
#         if heading_diff <= 180:
#             set_direction(FORWARD)
#         else:
#             set_direction(REVERSE)

#         step()
#         print(get_heading())
#         print(Desired_Heading)

# Set microstepping mode # currently unnessicary, gotta figure out microstepping v full steps
# def get_microstep_div(remaining_angle):
#     """Determine the appropriate microstep division."""
#     if remaining_angle > 18:
#         return 8    # Coarse movement (1/8 step)
#     elif remaining_angle > 10:
#         return 2    # Medium movement (1/2 step)
#     elif remaining_angle > 5:
#         return 4    # Finer movement (1/4 step)
#     else:
#         return 16   # Precision movement (1/16 step)

def get_step_delay(remaining_angle):
    """Adjust step delay to slow down smoothly as it nears the target."""
    return MAX_STEP_DELAY - (MAX_STEP_DELAY - MIN_STEP_DELAY) * math.exp(-0.1 * remaining_angle)

def gotoheading(Desired_Heading):
    """Move stepper to the desired heading using adaptive microstepping and step delays."""
    global acceptable_range 

    while abs(get_heading() - Desired_Heading) > 0.1:  # Stop when close enough
        current_heading = get_heading()
        heading_diff = (Desired_Heading - current_heading) % 360

        # Apply the dead zone: if the difference is within the acceptable range, break the loop
        if heading_diff <= acceptable_range or (360 - heading_diff) <= acceptable_range:
            print(f"Target reached: {current_heading:.2f}°")
            break  # Stop if we're within the acceptable range

        # Determine the shortest direction
        if heading_diff <= 180:
            set_direction(FORWARD)
        else:
            set_direction(REVERSE)
            heading_diff = 360 - heading_diff  # Adjust for reverse direction

        # microstep = get_microstep_div(heading_diff) # currently unnessicary, gotta figure out microstepping v full steps
        set_microstep_div(8)
        # Tweak step delay
        step_delay = get_step_delay(heading_diff)  # Dynamically adjust step delay
        
        # set_microstep_div(microstep)  # Set microstepping mode # currently unnessicary, gotta figure out microstepping v full steps
        step(step_delay)  # Execute step
        # print(f"Current: {current_heading:.2f}° | Target: {Desired_Heading}° | Remaining: {heading_diff:.2f}° | Microstep: 8 | Step Delay: {step_delay} | Slop: ±{acceptable_range} Degrees")



# run though a list of headings, avoid looping around while I dont have a slipring installed
# while True:
#     headings = [0, 90, 180, 270, 45, 120, 30, 320]
#     # for item in headings:
#     gotoheading(random.choice(headings))
#     time.sleep(5.0)


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
                gotoheading(data["heading"])

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