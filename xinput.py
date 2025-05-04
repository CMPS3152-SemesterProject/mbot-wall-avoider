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
max_speed = 456      # Maximum speed limit
current_speed = 0    # Current speed (controlled by triggers)
direction = 1        # 1 for forward, -1 for backward


def setup():
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
    global base_speed, current_speed, direction
    
    # Get current joystick values for continuous control
    left_x = joystick.get_axis(0)  # Left/Right on left stick for steering
    left_trigger = (joystick.get_axis(4) + 1) / 2  # Convert -1 to 1 range to 0 to 1 (acceleration)
    right_trigger = (joystick.get_axis(5) + 1) / 2  # Convert -1 to 1 range to 0 to 1 (deceleration/reverse)
    
    # Apply deadzone to steering to avoid drift when joystick is near center
    steering_deadzone = 0.15
    if abs(left_x) < steering_deadzone:
        left_x = 0
    
    # Handle acceleration with left trigger
    if left_trigger > 0.1:  # If left trigger is pressed
        # Calculate forward speed based on trigger pressure
        current_speed = int(left_trigger * base_speed)
        direction = 1  # Forward direction
    
    # Handle deceleration/reverse with right trigger (overrides left trigger if both pressed)
    if right_trigger > 0.1:  # If right trigger is pressed
        # Calculate reverse speed based on trigger pressure
        current_speed = int(right_trigger * base_speed)
        direction = -1  # Reverse direction
    
    # If neither trigger is pressed, gradually slow down
    if left_trigger <= 0.1 and right_trigger <= 0.1:
        current_speed = max(0, current_speed - 2)  # Gradual deceleration
    
    # Ensure we don't exceed max speed
    current_speed = min(current_speed, max_speed)
    
    # If we're not moving at all, just stop the motors
    if current_speed == 0:
        control.stop()
    else:
        # Car-like steering: Calculate differential speeds based on steering angle
        # At center position (left_x = 0), both motors run at the same speed
        # When turning, the inside wheel slows down proportionally to the turn angle
        
        # Scale the steering factor (how much the inner wheel slows down)
        steering_factor = abs(left_x) * 0.8  # 0 to 0.8 (max 80% reduction for inner wheel)
        
        if left_x > 0:  # Turning right
            # Right turn: left motor at full speed, right motor reduced
            left_motor_speed = current_speed * direction
            right_motor_speed = current_speed * (1 - steering_factor) * direction
        elif left_x < 0:  # Turning left
            # Left turn: right motor at full speed, left motor reduced
            left_motor_speed = current_speed * (1 - steering_factor) * direction
            right_motor_speed = current_speed * direction
        else:  # Going straight
            left_motor_speed = current_speed * direction
            right_motor_speed = current_speed * direction
        
        # Apply motor speeds
        control.encoder_left.run(int(left_motor_speed))
        control.encoder_right.run(int(-right_motor_speed))  # Negative due to motor orientation
        
        # Debug output
        print(f"Speed: {current_speed}, Direction: {'Forward' if direction > 0 else 'Reverse'}")
        print(f"Steering: {left_x:.2f}, Left Motor: {int(left_motor_speed)}, Right Motor: {int(-right_motor_speed)}")
    
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
                    current_speed = 0
                case 3:
                    print("Button Y down")
                    # Reset base speed to default
                    base_speed = 50
                case 4:  # RB
                    print("Increasing base speed")
                    base_speed = min(base_speed + 10, max_speed)
                    print(f"Base speed: {base_speed}")
                case 5:  # LB
                    print("Decreasing base speed")
                    base_speed = max(base_speed - 10, 10)
                    print(f"Base speed: {base_speed}")
                case 6:
                    print("Button OVERLAY down")
                case 7:
                    print("Button MENU down")
                case 10:
                    print("Button XBOX down")
                case _:
                    print(event.button)
        elif event.type == JOYBUTTONUP:
            # Handle button up events if needed
            pass


def entry_point():
    try:
        board.set_tone(50, 500)
        setup()
        board.set_tone(80, 500)
        print("Controller ready. Car-like controls enabled.")
        print("Left thumbstick: steering (left/right)")
        print("Left trigger: accelerate forward")
        print("Right trigger: accelerate backward")
        print("Press X (button 2) to stop motors.")
        print("Press LB/RB to decrease/increase base speed.")
        while True:
            main_loop()
            sleep(0.05)

    except KeyboardInterrupt:
        # turn the motors off
        control.stop()
        print("\nExiting application\n")
        # exit the application
        exit(0)
