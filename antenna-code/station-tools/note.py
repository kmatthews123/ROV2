import board
import digitalio
import time

def set_direction(direction_pin, direction):
    """Set motor direction"""
    direction_pin. value = direction

def step(step_pin):
    """Generate a single step pulse"""
    step_pin.value = True
    time.sleep(0.001)  # Pulse width
    step_pin.value = False

def initialize_motor():
    """Initialize motor settings (microstepping, etc.)"""
    MS1 = digitalio.DigitalInOut(board.D3)
    MS1.direction = digitalio.Direction.OUTPUT
    MS1.value = False
    
    MS2 = digitalio.DigitalInOut(board.D2) 
    MS2.direction = digitalio.Direction.OUTPUT
    MS2.value = True

def check_endstops(endstop_plus, endstop_minus, direction_pin):
    """Check endstop status and reverse direction if needed"""
    debounce_time = 0.1
    step_delay = 0.002
    
    last_plus = False
    last_minus = False
    last_check = 0
    
    while True:
        current_time = time.time()
        
        # Debounce endstop inputs
        if current_time - last_check > debounce_time:
            plus_triggered = not endstop_plus.value
            minus_triggered = not endstop_minus.value
            
            if plus_triggered != last_plus or minus_triggered != last_minus:
                if plus_triggered:
                    print("Plus endstop triggered, reversing direction to reverse.")
                    set_direction(direction_pin, True)  # REVERSE
                elif minus_triggered:
                    print("Minus endstop triggered, reversing direction to forward.")
                    set_direction(direction_pin, False)  # FORWARD
                
                last_plus = plus_triggered
                last_minus = minus_triggered
                last_check = current_time
            
            time.sleep(step_delay)

def run_motor():
    """Main motor control loop"""
    try:
        while True:
            step(step_pin)
    except KeyboardInterrupt:
        print("Program stopped by user")

# Note: The pin declarations would be handled outside these functions
# in the main program where you initialize your digitalio objects.


# Pin initialization (would be outside the function definitions)
direction_pin = digitalio.DigitalInOut(board.D0)
step_pin = digitalio.DigitalInOut(board.D1)
endstop_plus = digitalio.DigitalInOut(board.D6)
endstop_minus = digitalio.DigitalInOut(board.D7)

# Set up pin directions
direction_pin.direction = digitalio.Direction.OUTPUT
step_pin.direction = digitalio.Direction.OUTPUT

endstop_plus.direction = digitalio.Direction.INPUT
endstop_plus.pull = digitalio.Pull.UP

endstop_minus.direction = digitalio.Direction.INPUT 
endstop_minus.pull = digitalio.Pull.UP

# Initialize motor settings
initialize_motor()

# Start motor control
run_motor()