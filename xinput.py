import pygame
from pygame.constants import JOYBUTTONDOWN, JOYBUTTONUP, JOYAXISMOTION
import makeblock
from EncoderController import EncoderController
from makeblock.boards import MeAuriga
from sys import exit
from time import sleep

# -------------------------
#   Connect to Me Auriga
# -------------------------
# Fallback to COM4 if not using BLE
makeblock.add_port("COM3")
board = MeAuriga.connect(BLE=True)

MOTOR0_PIN = 1
MOTOR1_PIN = 2
control = EncoderController(board, MOTOR0_PIN, MOTOR1_PIN)

pygame.init() # Initialize the runtime
joystick = pygame.joystick.Joystick(0)  # First joystick detected

# Motor speed and direction settings
base_speed = 50      # Default base speed
max_speed = 150      # Maximum speed limit
speed_factor = 1.0   # Speed multiplier from left trigger
direction = 1        # 1 for forward, -1 for backward (controlled by right trigger)

def setup():
    # motor0.on()
    joystick.init()  # Initialize the joystick
    print("Attached: " + joystick.get_name())


'''
# Xbox Joystick Axis
Axis:
   - 0: Left Stick X (Left/Right)
      - Left (-1)
      - Right (1)
      - Center (0)
   - 1: Left Stick Y (Up/Down)
      - Up (-1)
      - Down (1)
      - Center (0)
   - 2: Right Stick X (Left/Right)
   - 3: Right Stick Y (Up/Down)
   - 4: Left Trigger (0 to 1)
   - 5: Right Trigger (0 to 1)
'''


def main_loop():
    global base_speed, speed_factor, direction
    
    # Get current joystick values for continuous control
    left_x = joystick.get_axis(0)  # Left/Right on left stick
    left_y = joystick.get_axis(1)  # Up/Down on left stick
    left_trigger = (joystick.get_axis(4) + 1) / 2  # Convert -1 to 1 range to 0 to 1
    right_trigger = (joystick.get_axis(5) + 1) / 2  # Convert -1 to 1 range to 0 to 1
    
    # Update speed based on left trigger (increase speed as trigger is pressed)
    speed_factor = 1.0 + left_trigger  # Scale from 1.0 to 2.0
    
    # Set direction based on right trigger (reverse when pressed)
    if right_trigger > 0.5:  # If right trigger is pressed more than halfway
        direction = -1
    else:
        direction = 1
    
    # Calculate final speed
    current_speed = min(int(base_speed * speed_factor), max_speed)
    
    # Apply deadzone to avoid drift when joystick is near center
    deadzone = 0.15
    if abs(left_x) < deadzone:
        left_x = 0
    if abs(left_y) < deadzone:
        left_y = 0
    
    # Control logic based on left joystick position
    if abs(left_x) < deadzone and abs(left_y) < deadzone:
        # Joystick is in neutral position - stop motors
        control.stop()
    else:
        # Calculate motor speeds based on joystick position
        # For differential steering:
        # Left motor = Y axis value + X axis value
        # Right motor = Y axis value - X axis value
        left_motor_value = int((-left_y + left_x) * current_speed) * direction
        right_motor_value = int((-left_y - left_x) * current_speed) * direction
        
        # Apply motor speed
        control.encoder_left.run(left_motor_value)
        control.encoder_right.run(-right_motor_value)  # Negative due to motor orientation
        
        # Debug output
        print(f"Speed: {current_speed}, Direction: {'Forward' if direction == 1 else 'Reverse'}")
        print(f"Left Motor: {left_motor_value}, Right Motor: {right_motor_value}")
    
    # Process other events
    for event in pygame.event.get():
        if event.type == JOYBUTTONDOWN:
            match event.button:
                case 0:
                    print("Button A down")
                case 1:
                    print("Button B down")
                case 2:
                    print("Turning off motors")
                    control.stop()
                case 3:
                    print("Button Y down")
                    # Reset base speed to default
                    base_speed = 50
                case 4:  # RB
                    print("Increasing base speed")
                    base_speed = min(base_speed + 10, max_speed)
                case 5:  # LB
                    print("Decreasing base speed")
                    base_speed = max(base_speed - 10, 10)
                case 6:
                    print("Button OVERLAY down")
                case 7:
                    print("Button MENU down")
                case 10:
                    print("Button XBOX down")
                case _:
                    print(event.button)
        elif event.type == JOYBUTTONUP:
            match event.button:
                case 0:
                    print("Button A up")
                case 1:
                    print("Button B up")
                case 2:
                    print("Button X up")
                case 3:
                    print("Button Y up")
                case 4:
                    print("Button RB up")
                case 5:
                    print("Button LB up")
                case 6:
                    print("Button OVERLAY up")
                case 7:
                    print("Button MENU up")
                case 10:
                    print("Button XBOX up")
                case _:
                    print(event.button)


def entry_point():
    try:
        board.set_tone(50, 500)
        setup()
        board.set_tone(80, 500)
        print("Controller ready. Use left joystick to move.")
        print("Left trigger increases speed, right trigger reverses direction.")
        print("Press X (button 2) to stop motors.")
        print("Press LB/RB to decrease/increase base speed.")
        while True:
            main_loop()
            sleep(0.01)

    except KeyboardInterrupt:
        # turn the motors off
        control.stop()
        print("\nExiting application\n")
        # exit the application
        exit(0)
