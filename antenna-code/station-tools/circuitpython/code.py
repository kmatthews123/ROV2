# writen by keith matthews using examples from adafruit librarys

import board #type: ignore
import digitalio #type: ignore
import time
import math
import adafruit_lis2mdl # type: ignore
import usb_cdc # type: ignore

# Setup pins as outputs or inputs

# Stepper
# Define GPIO pins for motor control and endstops
direction_pin = digitalio.DigitalInOut(board.D0)
step_pin = digitalio.DigitalInOut(board.D1)
direction_pin.direction = digitalio.Direction.OUTPUT
step_pin.direction = digitalio.Direction.OUTPUT
# Define motor directions at start of program
FORWARD = False
REVERSE = True
# Setup microstepping pins
MS1 = digitalio.DigitalInOut(board.D3)
MS2 = digitalio.DigitalInOut(board.D2)
MS1.direction = digitalio.Direction.OUTPUT
MS2.direction = digitalio.Direction.OUTPUT

# endstops
endstop_plus = digitalio.DigitalInOut(board.D6)
endstop_minus = digitalio.DigitalInOut(board.D7)
endstop_plus.direction = digitalio.Direction.INPUT
endstop_minus.direction = digitalio.Direction.INPUT
endstop_plus.pull = digitalio.Pull.UP
endstop_minus.pull = digitalio.Pull.UP

#magnetometer
# i2c = board.I2C()
i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
magnetometer = adafruit_lis2mdl.LIS2MDL(i2c)

#USB serial data
#Access the USB serial port
usb_serial = usb_cdc.data

# Variables
# magnetometer
hardiron_calibration = [[-15.15, 16.5], [8.7, 40.5], [-17.55, -7.35]] # magnetometer calibration value
# stepper
step_delay = 0.002  # Time between steps (adjust for speed)
# endstops
debounce_time = 0.001  # Debounce time in seconds
# Motor state tracking
current_step_position = 0  # Tracks the stepper's current step position
target_position = 0

# Calibration global variables
calibration_complete = False
steps_around = 0
minus_heading = 0
plus_heading = 0
arc_len = 0
avg_plus = 0
avg_minus = 0

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
# # step selection table
# # |  MS1  |  MS2  | Microstep Resolution
# # |  False |  False | 1/8 
# # |  False |  True  | 1/2
# # |  True  |  False | 1/4
# # |  True  |  True  | 1/16
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
        print(f"set microstep value to {step_div}")
    else:
        global MS1, MS2
        MS1.value = False
        MS2.value = False
        print("unknown microstep value selected, setting to 1/8")

        
def set_direction(direction):
    direction_pin.value = direction

def step():
    step_pin.value = True
    time.sleep(0.001)  # Pulse width
    step_pin.value = False

def calibrate():
    global calibration_complete, steps_around, minus_heading, plus_heading
    if calibration_complete:
        calibration_complete = False
        steps_around = 0
        minus_heading = 0
    
    # Move forward until endplus is hit
    set_direction(FORWARD)
    while True:
        step()
        time.sleep(step_delay)
        if not endstop_plus.value:  # Endplus pressed
            break
    # Wait for debounce to ensure the switch is released
    time.sleep(debounce_time)
    plus_heading = get_heading()
    print(f"plus heading = {plus_heading}")
    
    # Now move backward until endminus is hit, counting steps
    set_direction(REVERSE)
    while True:
        step()
        steps_around += 1
        time.sleep(step_delay)
        if not endstop_minus.value:  # Endminus pressed
            break
    # Ensure the switch is released before completing
    time.sleep(debounce_time)
    minus_heading = get_heading()
    print(f"minus heading = {minus_heading}")
    
    calibration_complete = True

def get_heading():
    magvals = magnetometer.magnetic
    normvals = normalize(magvals)
    # print("magnetometer: %s -> %s" % (magvals, normvals))
    # we will only use X and Y for the compass calculations, so hold it level!
    compass_heading = float(math.atan2(normvals[1], normvals[0]) * 180.0 / math.pi)
    # compass_heading is between -180 and +180 since atan2 returns -pi to +pi
    # this translates it to be between 0 and 360
    compass_heading += 180
    #print("Heading:", compass_heading)
    return compass_heading

def angle_between_headings(heading1, heading2):
    # Calculate the raw difference
    angle = abs(heading2 - heading1) % 360
    
    # If the angle is greater than 180°, we take the complementary angle
    if angle > 180:
        angle = 360 - angle
    
    return angle

def preform_calibration(num_passes, step_division):
    # lists of calibration values for each itteration
    global avg_step_value, arc_len, avg_plus, avg_minus
    cal_values = []
    list_plus = []
    list_minus = []
    set_microstep_div(step_division)
    # run calibration, record values
    for i in range (num_passes):
        calibrate()
        cal_values.append(steps_around)
        list_plus.append(plus_heading)
        list_minus.append(minus_heading)
    avg_step_value = round(sum(cal_values) / len(cal_values))
    avg_minus = round(sum(list_minus) / len(list_minus))
    avg_plus = round(sum(list_plus) / len(list_plus))
    arc_len = angle_between_headings(avg_plus, avg_minus)
    print(f"Average steps between stops: {avg_step_value}")
    print(f"Arc length = {arc_len}")


def goto_steps(num_steps, step_divison):
    set_microstep_div(step_divison)
    if num_steps < 0 :
        set_direction(REVERSE)
        for i in range(abs(num_steps)):
            step()
            time.sleep(step_delay)
    else:
        set_direction(FORWARD)
        for i in range(abs(num_steps)):
            step()
            time.sleep(step_delay)

# while True:
preform_calibration(1, 8)
preform_calibration(2, 4)
preform_calibration(2, 2)
preform_calibration(2, 16)
#     goto_steps(-4000, 8)
#     print(f" heading 1 {get_heading()}")
#     goto_steps(4000, 8)
#     print(f" heading 2 {get_heading()}")
# while True:
    # preform_calibration(1, 8)
    # preform_calibration(2, 4)
    # preform_calibration(2, 2)
    # preform_calibration(2, 16)
#             time.sleep(step_delay)
#         val_invert -= 1