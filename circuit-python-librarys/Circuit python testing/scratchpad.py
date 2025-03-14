# # Working code
# # SPDX-FileCopyrightText: 2025 Liz Clark for Adafruit Industries
# # #
# SPDX-License-Identifier: MIT

#--- Magnetometer ---#
import math
import adafruit_lis2mdl # type: ignore

# magnetometer = adafruit_lis2mdl.LIS2MDL(i2c)
# # calibration for magnetometer X (min, max), Y and Z
# # hardiron_calibration = [[1000, -1000], [1000, -1000], [1000, -1000]]

#--- stepper control ---
import time
from time import sleep
import board
from digitalio import DigitalInOut, Direction

#--- neopixel ---
from rainbowio import colorwheel
import neopixel # type: ignore

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.3


i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
magnetometer = adafruit_lis2mdl.LIS2MDL(i2c)
# magnetometer calibration value
hardiron_calibration = [[-15.15, 16.5], [8.7, 40.5], [-17.55, -7.35]]

# This will take the magnetometer values, adjust them with the calibrations
# and return a new array with the XYZ values ranging from -100 to 100
def normalize(_magvals):

    ret = [0, 0, 0]

    for i, axis in enumerate(_magvals):

        minv, maxv = hardiron_calibration[i]

        axis = min(max(minv, axis), maxv)  # keep within min/max calibration

        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100

    return ret

# not using this yet
def calibrate():
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

def rainbow():
    for color_value in range(255):
        pixel[0] = colorwheel(color_value)
        

# direction and step pins as outputs
DIR = DigitalInOut(board.D0)
DIR.direction = Direction.OUTPUT
STEP = DigitalInOut(board.D1)
STEP.direction = Direction.OUTPUT

# step selection pin assingment
# step selection table
# |  MS1  |  MS2  | Microstep Resolution
# |  LOW  |  LOW  | 1/8
# |  LOW  |  HIGH | 1/2
# |  HIGH |  LOW  | 1/4
# |  HIGH |  HIGH | 1/16
MS1 = DigitalInOut(board.D3)
MS1.direction = Direction.OUTPUT
MS1.value = False
MS2 = DigitalInOut(board.D2)
MS2.direction = Direction.OUTPUT
MS2.value = False

# microstep mode, default is 1/8 so 8
# another ex: 1/16 microstep would be 16
microMode = 8
# modify the number below to tweak amount of steps in one revolution.
# I probably am not going to keep this
steps = 50 * microMode

while True:
    # change direction every loop
    DIR.value = not DIR.value
    # toggle STEP pin to move the motor
    for i in range(steps):
        STEP.value = True
        time.sleep(0.001)
        STEP.value = False
        time.sleep(0.001)
        magvals = magnetometer.magnetic
        normvals = normalize(magvals)
        print("magnetometer: %s -> %s" % (magvals, normvals))
        # we will only use X and Y for the compass calculations, so hold it level!
        compass_heading = int(math.atan2(normvals[1], normvals[0]) * 180.0 / math.pi)
        # compass_heading is between -180 and +180 since atan2 returns -pi to +pi
        # this translates it to be between 0 and 360
        compass_heading += 180
        print("Heading:", compass_heading)
        
    print("rotated! now reverse")
    print("heading: ", compass_heading)
    rainbow()

    time.sleep(0.1)

