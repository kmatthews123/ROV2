import board #type: ignore
import digitalio #type: ignore
import time

# Setup pins as outputs or inputs
# Stepper
# Define GPIO pins for motor control and endstops
direction_pin = digitalio.DigitalInOut(board.D0)
step_pin = digitalio.DigitalInOut(board.D1)
direction_pin.direction = digitalio.Direction.OUTPUT
step_pin.direction = digitalio.Direction.OUTPUT
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

# Variables
# Define microstepping values
# # step selection table
# # |  MS1  |  MS2  | Microstep Resolution
# # |  False |  False | 1/8 
# # |  False |  True  | 1/2
# # |  True  |  False | 1/4
# # |  True  |  True  | 1/16
# MS1.value = False
# MS2.value = False

step_delay = 0.002  # Time between steps (adjust for speed)
debounce_time = 0.1  # Debounce time in seconds

# Define motor directions
FORWARD = False
REVERSE = True

# Variables
# Define microstepping values
# # step selection table
# # |  MS1  |  MS2  | Microstep Resolution
# # |  False |  False | 1/8 
# # |  False |  True  | 1/2
# # |  True  |  False | 1/4
# # |  True  |  True  | 1/16
# MS1 = False
# MS2 = False

# Calibration global variables
calibration_complete = False
steps_around = 0

def set_microstep_div(step_div):
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
        

def set_direction(direction):
    direction_pin.value = direction

def step():
    step_pin.value = True
    time.sleep(0.001)  # Pulse width
    step_pin.value = False

def calibrate():
    global calibration_complete, steps_around
    if calibration_complete:
        calibration_complete = False
        steps_around = 0
    
    # Move forward until endplus is hit
    set_direction(FORWARD)
    while True:
        step()
        time.sleep(step_delay)
        if not endstop_plus.value:  # Endplus pressed
            break
    # Wait for debounce to ensure the switch is released
    time.sleep(debounce_time)
    
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
    
    calibration_complete = True
    print(f"Calibration complete. Steps between stops: {steps_around}")
    steps_around

def preform_calibration(num_passes, step_division):
    cal_values = []
    set_microstep_div(step_division)
    for i in range (num_passes):
        calibrate()
        cal_values.append(steps_around)
    print(cal_values)
    avg_cal_value = round(sum(cal_values) / len(cal_values))
    print(avg_cal_value)


print("1/2 microsteps")
preform_calibration(2, 2)
print("1/4 microsteps")
preform_calibration(2, 4)
print("1/8 microsteps")
preform_calibration(2, 8)
print("1/16 microsteps")
preform_calibration(2, 16)
