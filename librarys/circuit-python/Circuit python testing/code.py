###-------------------------------------------------------------------------------------------
# # neopixel plus magentometer readings
# # SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# # SPDX-License-Identifier: MIT
# """CircuitPython status NeoPixel rainbow example."""
# import time
# from time import sleep
# import board
# from rainbowio import colorwheel
# import neopixel

# import busio
# import adafruit_lsm303_accel
# import adafruit_lis2mdl

# pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
# pixel.brightness = 0.3


# i2c = busio.I2C(board.SCL, board.SDA)
# mag = adafruit_lis2mdl.LIS2MDL(i2c)
# accel = adafruit_lsm303_accel.LSM303_Accel(i2c)


# def rainbow(delay):
#     for color_value in range(255):
#         pixel[0] = colorwheel(color_value)
#         time.sleep(delay)


# while True:
#     rainbow(0.02)
#     print("Acceleration (m/s^2): X=%0.3f Y=%0.3f Z=%0.3f"%accel.acceleration)
#     print("Magnetometer (micro-Teslas)): X=%0.3f Y=%0.3f Z=%0.3f"%mag.magnetic)
#     print("")
#     sleep(0.1)

### -----------------------------------------------------------------------------------------
# Compass readout
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries

# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries

# SPDX-License-Identifier: MIT


# """ Display compass heading data from a calibrated magnetometer """


# import time

# import math

# import board

# import adafruit_lis2mdl


# i2c = board.I2C()  # uses board.SCL and board.SDA

# # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# sensor = adafruit_lis2mdl.LIS2MDL(i2c)


# # You will need the calibration values from your magnetometer calibration

# # these values are in uT and are in X, Y, Z order (min and max values).

# #

# # To get these values run the lis2mdl_calibrate.py script on your device.

# # Twist the device around in 3D space while it calibrates. It will print

# # some calibration values like these:

# # ...

# # Calibrating - X:    -46.62, Y:    -22.33, Z:    -16.94 uT

# # ...

# # Calibration complete:

# # hardiron_calibration = [[-63.5487, 33.0313], [-40.5145, 53.8293], [-43.7153, 55.5101]]

# #

# # You need t copy your own value for hardiron_calibration from the output and paste it

# # into this script here:

# hardiron_calibration = [[-15.15, 16.5], [8.7, 40.5], [-17.55, -7.35]]



# # This will take the magnetometer values, adjust them with the calibrations

# # and return a new array with the XYZ values ranging from -100 to 100

# def normalize(_magvals):

#     ret = [0, 0, 0]

#     for i, axis in enumerate(_magvals):

#         minv, maxv = hardiron_calibration[i]

#         axis = min(max(minv, axis), maxv)  # keep within min/max calibration

#         ret[i] = (axis - minv) * 200 / (maxv - minv) + -100

#     return ret



# while True:

#     magvals = sensor.magnetic

#     normvals = normalize(magvals)

#     print("magnetometer: %s -> %s" % (magvals, normvals))


#     # we will only use X and Y for the compass calculations, so hold it level!

#     compass_heading = int(math.atan2(normvals[1], normvals[0]) * 180.0 / math.pi)

#     # compass_heading is between -180 and +180 since atan2 returns -pi to +pi

#     # this translates it to be between 0 and 360

#     compass_heading += 180


#     print("Heading:", compass_heading)

#     time.sleep(0.1)


###-------------------------------------------------------------------------------------------------------------------------
# # Calibrate sensor
# # # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries

# # # SPDX-License-Identifier: MIT

# # """ Calibrate the magnetometer and print out the hard-iron calibrations """


# import time

# import board

# import adafruit_lis2mdl


# i2c = board.I2C()  # uses board.SCL and board.SDA

# #i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# magnetometer = adafruit_lis2mdl.LIS2MDL(i2c)


# # calibration for magnetometer X (min, max), Y and Z

# hardiron_calibration = [[1000, -1000], [1000, -1000], [1000, -1000]]



# def calibrate():

#     start_time = time.monotonic()


#     # Update the high and low extremes

#     while time.monotonic() - start_time < 10.0:

#         magval = magnetometer.magnetic

#         print("Calibrating - X:{0:10.2f}, Y:{1:10.2f}, Z:{2:10.2f} uT".format(*magval))

#         for i, axis in enumerate(magval):

#             hardiron_calibration[i][0] = min(hardiron_calibration[i][0], axis)

#             hardiron_calibration[i][1] = max(hardiron_calibration[i][1], axis)

#     print("Calibration complete:")

#     print("hardiron_calibration =", hardiron_calibration)



# print("Prepare to calibrate! Twist the magnetometer around in 3D in...")

# print("3...")

# time.sleep(1)

# print("2...")

# time.sleep(1)

# print("1...")

# time.sleep(1)


# calibrate()

# Calibration results
# hardiron_calibration = [[-15.15, 16.5], [8.7, 40.5], [-17.55, -7.35]]

###------------------------------------------------------------------------------------
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

